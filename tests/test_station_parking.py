"""Full station planner tests use only original authored map/model fixtures."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.rest_stops import inspect_rest_triggers
from ats_road_trip.station_parking import plan_station_parking,render_station_plan
from ats_road_trip.station_parking.validation import _mesh_checks
from ats_road_trip.station_parking.trigger import append_car_parking_polygon
from tests.test_bulk_fuel import resources as fuel_resources, SECTOR, PPD
from tests.test_station_geometry import station_descriptor
from tests.test_rest_stops import ACTIONS


def mesh_text():
    ground=[(-30.,0.,30.),(40.,0.,30.),(40.,0.,-40.),(-30.,0.,-40.)]
    paint=[];triangles=[]
    for center in (5.,8.,11.,14.):
        i=len(paint);paint.extend([(center-.1,.01,-9.),(center+.1,.01,-9.),
                                  (center+.1,.01,-3.),(center-.1,.01,-3.)])
        triangles.extend([(i,i+1,i+2),(i,i+2,i+3)])
    result=['Header {',' FormatVersion: 5',' Source: "authored fixture"',' Type: "Model"',' Name: "station"','}',
            'Global {',f' VertexCount: {len(ground)+len(paint)}',f' TriangleCount: {2+len(triangles)}',
            ' MaterialCount: 2',' PieceCount: 2',' PartCount: 1',' BoneCount: 0',' LocatorCount: 0',' Skeleton: "station.pis"','}']
    for alias in ('asphalt','paint'):
        result.extend(['Material {',f' Alias: "{alias}"',' Effect: "eut2.dif.spec"','}'])
    for index,(positions,faces) in enumerate([(ground,[(0,1,2),(0,2,3)]),(paint,triangles)]):
        result.extend(['Piece {',f' Index: {index}',f' Material: {index}',f' VertexCount: {len(positions)}',
                       f' TriangleCount: {len(faces)}',' StreamCount: 1',' Stream {','  Format: FLOAT3','  Tag: "_POSITION"'])
        result.extend(f'  {i} ( {x} {y} {z} )' for i,(x,y,z) in enumerate(positions))
        result.extend([' }',' Triangles {'])
        result.extend(f'  {i} ( {a} {b} {c} )' for i,(a,b,c) in enumerate(faces))
        result.extend([' }','}'])
    result.extend(['Part {',' Name: "part1"',' PieceCount: 2',' LocatorCount: 0',' Pieces: 0 1',' Locators:','}'])
    return '\n'.join(result)+'\n'


def unmarked_mesh_text():
    """Station model with only asphalt: no paint material or parked locators."""
    result=['Header {',' FormatVersion: 5',' Source: "authored fixture"',' Type: "Model"',' Name: "station"','}',
            'Global {',' VertexCount: 4',' TriangleCount: 2',' MaterialCount: 1',' PieceCount: 1',
            ' PartCount: 1',' BoneCount: 0',' LocatorCount: 0',' Skeleton: "station.pis"','}',
            'Material {',' Alias: "asphalt"',' Effect: "eut2.dif.spec"','}',
            'Piece {',' Index: 0',' Material: 0',' VertexCount: 4',' TriangleCount: 2',' StreamCount: 1',
            ' Stream {','  Format: FLOAT3','  Tag: "_POSITION"',
            '  0 ( -30.0 0.0 30.0 )','  1 ( 40.0 0.0 30.0 )',
            '  2 ( 40.0 0.0 -40.0 )','  3 ( -30.0 0.0 -40.0 )',' }',' Triangles {',
            '  0 ( 0 1 2 )','  1 ( 0 2 3 )',' }','}',
            'Part {',' Name: "part1"',' PieceCount: 1',' LocatorCount: 0',' Pieces: 0',' Locators:','}']
    return '\n'.join(result)+'\n'


def source_resources():
    contents=fuel_resources([((-4.,.1,0.),0),((-4.,.1,0.),1)])
    ppd=contents[PPD];header=list(struct.unpack_from('<24I',ppd))
    mapped=station_descriptor();mh=struct.unpack_from('<24I',mapped)
    map_records=mapped[mh[20]:mh[21]]
    insertion=header[20]
    header[8]=mh[8]
    for i in (21,22,23):header[i]+=len(map_records)
    ppd=struct.pack('<24I',*header)+ppd[96:insertion]+map_records+ppd[insertion:]
    ppd,_=append_car_parking_polygon(ppd,[(-15.,0.,-28.),(-5.,0.,-28.),(-5.,0.,-22.),(-15.,0.,-22.)])
    ppd=bytearray(ppd);ph=struct.unpack_from('<24I',ppd)
    for i in range(ph[9]):struct.pack_into('<Q',ppd,ph[21]+48*i+4,token('hud_parking'))
    contents[PPD]=bytes(ppd)
    contents['prefab/test/station.pmg']=b'Original authored source model identity, not game data'
    contents['def/world/trigger_action.sii']=ACTIONS
    contents['def/data_context.sii']=b'SiiNunit\n{\ndata_context : context.fixture {\n target_data[]: prefab.02003\n tags[]: gas_station\n}\n}\n'
    return contents


class StationPlannerTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.packages=[]
        self.addCleanup(lambda:[p.close() for p in self.packages])
        self.original=source_resources();self.mesh=mesh_text();self.number=0

    def make_stack(self,contents=None):
        self.number+=1;path=self.root/f'source-{self.number}.scs'
        contents=contents or self.original
        with zipfile.ZipFile(path,'w') as archive:
            for name,data in contents.items():archive.writestr(name,data)
        package=Package(path);self.packages.append(package)
        config={'schema_version':1,'processor':'station_parking','station_id':'synthetic-station',
                'map_name':'Fixture Map','game_version':'1.61.3.18','method':'painted_bays',
                'sector':SECTOR,'prefab_uid':'0x64','model_geometry':'prefab/test/station.pmg',
                'fingerprints':{'source_archive':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'sector':hashlib.sha256(contents[SECTOR]).hexdigest(),'descriptor':hashlib.sha256(contents[PPD]).hexdigest(),
                    'model_geometry':hashlib.sha256(contents['prefab/test/station.pmg']).hexdigest(),
                    'mesh':hashlib.sha256(self.mesh.encode()).hexdigest()},
                'mesh_materials':{'ground':['asphalt'],'paint':['paint']},'parameters':{}}
        return package,ResourceStack([package]),config

    def plan(self,stack,config,package):
        return plan_station_parking(stack,config,self.mesh,map_package=str(package.path),game_version='1.61.3.18')

    def test_painted_model_drives_new_geometry_and_all_original_sector_records_survive(self):
        package,stack,config=self.make_stack()
        report,changes=self.plan(stack,config,package)
        self.assertTrue(report['coverage']['complete'],report['coverage'])
        self.assertEqual(report['selected']['bay_count'],3)
        original=self.original[SECTOR];changed=changes[SECTOR]
        prefab=parse_sector(original).prefabs[0]
        allowed=set(range(prefab.offset+57,prefab.offset+65))
        self.assertEqual(len(original),len(changed))
        self.assertTrue(all(i in allowed for i,(a,b) in enumerate(zip(original,changed)) if a!=b))
        before=parse_sector(original);after=parse_sector(changed)
        self.assertEqual([n.raw for n in before.nodes],[n.raw for n in after.nodes])
        self.assertEqual([original[i.offset:i.end] for i in before.services],
                         [changed[i.offset:i.end] for i in after.services])
        new_ppd=next(value for path,value in changes.items() if path.endswith('.ppd'))
        header=struct.unpack_from('<24I',self.original[PPD]);extra=len(new_ppd)-len(self.original[PPD])
        self.assertEqual(new_ppd[96:header[22]],self.original[PPD][96:header[22]])
        self.assertEqual(new_ppd[header[22]+extra:],self.original[PPD][header[22]:])
        self.assertEqual(len(inspect_rest_triggers(new_ppd)),2)
        self.assertTrue(any(path.startswith('def/data_context.') for path in changes))
        self.assertEqual(report['context_preservation']['aliases'][0]['tags'],['gas_station'])
        svg=render_station_plan(report)
        self.assertIn('<svg',svg);self.assertIn('synthetic-station',svg)
        self.assertNotIn('nan',svg.lower())

    def test_unmarked_method_never_uses_native_truck_polygon_as_candidate(self):
        package,stack,config=self.make_stack();config['method']='unmarked_geometry'
        report,changes=self.plan(stack,config,package)
        self.assertTrue(report['coverage']['complete'],report['coverage'])
        self.assertEqual(report['proposal']['method'],'unmarked_map_geometry')
        chosen=report['selected']['polygon_xz']
        self.assertTrue(all(z>-15 for x,z in chosen))
        truck=report['original_rest_groups'][0]['vertices']
        self.assertNotEqual({(x,z) for x,z in chosen},{(x,z) for x,y,z in truck})
        self.assertTrue(changes)

    def test_unmarked_method_works_without_any_paint_material_or_piece(self):
        package,stack,config=self.make_stack();config['method']='unmarked_geometry'
        self.mesh=unmarked_mesh_text()
        config['mesh_materials']['paint']=[]
        config['fingerprints']['mesh']=hashlib.sha256(self.mesh.encode()).hexdigest()
        report,changes=self.plan(stack,config,package)
        self.assertTrue(report['coverage']['complete'],report['coverage'])
        self.assertEqual(report['proposal']['method'],'unmarked_map_geometry')
        self.assertGreaterEqual(len(report['selected']['polygon_xz']),3)
        self.assertTrue(changes)
        self.assertEqual(report['mesh_summary']['counts']['materials'],1)
        self.assertEqual(report['mesh_summary']['counts']['pieces'],1)
        self.assertEqual(report['mesh_summary']['locators'],[])
        original_triggers=inspect_rest_triggers(self.original[PPD])
        changed_ppd=next(value for path,value in changes.items() if path.endswith('.ppd'))
        changed_triggers=inspect_rest_triggers(changed_ppd)
        self.assertEqual(changed_triggers[:len(original_triggers)],original_triggers)
        self.assertIn(token('parking_car'),{group['action'] for group in changed_triggers})

    def test_painted_method_requires_a_nonempty_paint_alias_list(self):
        package,stack,config=self.make_stack();config['mesh_materials']['paint']=[]
        with self.assertRaisesRegex(ValueError,'paint'):
            self.plan(stack,config,package)

    def test_repeated_planning_is_identical_including_alias_contexts_and_svg(self):
        package,stack,config=self.make_stack()
        first=self.plan(stack,config,package);second=self.plan(stack,config,package)
        self.assertEqual(first,second)
        self.assertEqual(render_station_plan(first[0]),render_station_plan(second[0]))

    def test_source_sector_descriptor_model_and_mesh_drift_are_refused(self):
        package,stack,config=self.make_stack()
        for label in ('source_archive','sector','descriptor','model_geometry','mesh'):
            changed=deepcopy(config);changed['fingerprints'][label]='0'*64
            with self.subTest(label=label),self.assertRaisesRegex(ValueError,'SHA-256'):
                self.plan(stack,changed,package)

    def test_wrong_station_version_and_parameters_are_refused(self):
        package,stack,config=self.make_stack()
        for field,value in [('prefab_uid','0x99'),('game_version','1.61.3.19'),('parameters',{'drawn_rectangle':True})]:
            changed=deepcopy(config);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.plan(stack,changed,package)

    def test_overlapping_native_car_trigger_blocks_duplicate_generation(self):
        contents=dict(self.original)
        contents[PPD],_=append_car_parking_polygon(contents[PPD],[(4.,0.,-10.),(16.,0.,-10.),(16.,0.,-2.),(4.,0.,-2.)])
        package,stack,config=self.make_stack(contents)
        report,changes=self.plan(stack,config,package)
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(changes,{})
        self.assertIn('already_has_overlapping_native_car_rest',report['candidates'][0]['rejection_reasons'])

    def test_ambiguous_missing_surface_is_rejected_without_writer_fallback(self):
        package,stack,config=self.make_stack()
        config['mesh_materials']['ground']=['paint']
        report,changes=self.plan(stack,config,package)
        self.assertFalse(report['coverage']['complete']);self.assertFalse(changes)
        self.assertTrue(report['candidates'][0]['model_surface_checks']['missing_samples'])

    def test_model_clearance_rejects_vertical_obstacle_and_parked_vehicle(self):
        from ats_road_trip.station_parking.mesh import read_station_mesh
        mesh=read_station_mesh(self.mesh)
        mesh['materials'].append({'alias':'wall','effect':'eut2.dif.spec'})
        mesh['pieces'].append({'index':2,'material':'wall','positions':[(8.,0.,-8.),(8.,2.,-8.),(8.,2.,-4.)],
                               'triangles':[(0,1,2)]})
        mesh['locators'].append({'index':0,'hookup':'car.parked.physics','position':(10.,0.,-6.)})
        report=_mesh_checks(mesh,[(5.,-9.),(14.,-9.),(14.,-3.),(5.,-3.)],None,['asphalt'],['paint'])
        self.assertIn('model_geometry_intersects_car_clearance_volume',report['rejection_reasons'])
        self.assertIn('parked_vehicle_locator_exclusion',report['rejection_reasons'])


if __name__=='__main__':unittest.main()
