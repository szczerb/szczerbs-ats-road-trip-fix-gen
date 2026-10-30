"""Source-model obstacle policy tests using tiny authored map-sector resources."""
from pathlib import Path
from types import SimpleNamespace
import struct
import unittest
from unittest.mock import patch

from ats_road_trip.local_fuel import token
from ats_road_trip.truck_parking import obstacles

SECTOR='map/usa/sec+0000+0000.base'
NEIGHBOR='map/usa/sec+0001+0000.base'
OUTSIDE='map/usa/sec+0002+0000.base'
BANK={'sector':SECTOR,'vertices':[(0.,0.,0.),(10.,0.,0.),(10.,0.,25.),(0.,0.,25.)]}
OLD=[(0.,0.,0.),(10.,0.,0.),(10.,0.,10.),(0.,0.,10.)]

def row(poly,kind='static_model',sector=SECTOR):
    return {'uid':'0x1','sector':sector,'model_token':'0x2','model_path':'/model/props/object.pmd',
            'polygon_xz':poly,'bounds_xyz':[min(p[0] for p in poly),0.,min(p[1] for p in poly),
                                             max(p[0] for p in poly),1.,max(p[1] for p in poly)],'class':kind}

class MemoryStack:
    def __init__(self,values):
        self.values=values
        self.resources={p:(SimpleNamespace(path=Path('authored-fixture.scs')),None) for p in values}
    def read(self,path,**kwargs):return self.values[path]
    def text(self,path):return self.read(path).decode()
    def prefetch(self,*args,**kwargs):return None
    def matching(self,pattern):
        import re
        rx=re.compile(pattern);return sorted(p for p in self.resources if rx.fullmatch(p))

def model_sector(uid,bounds,model):
    header=struct.pack('<IQI',907,token('euro2'),3)
    common=struct.pack('<IQ10fIB',5,uid,*bounds,0,0)
    # Kind-5 payload: model token in its first 24-byte block, no refs, remaining fixed fields.
    payload=struct.pack('<QQQ',model,0,0)+struct.pack('<I',0)+bytes(36)
    return header+struct.pack('<I',1)+common+payload+struct.pack('<I',0)+struct.pack('<I',0)

def kdop(x0,x1,z0,z1,y0=0.,y1=1.):
    return (x0,y0,z0,(x0+z0)/2.,(x0-z1)/2.,x1,y1,z1,(x1+z1)/2.,(x1-z0)/2.)

class TruckObstaclePolicyTests(unittest.TestCase):
    def run_clear(self,models, *, old=OLD, bank=BANK):
        with patch.object(obstacles,'nearby_models',return_value=models):
            return obstacles.clear_bank(None,bank,original_vertices=old)

    def test_permanent_trash_box_blocks_newly_activated_space(self):
        added=row([(2.,12.),(4.,12.),(4.,14.),(2.,14.)])
        _,report=self.run_clear([added])
        self.assertEqual(report['state'],'blocked')
        self.assertEqual(len(report['blockers']),1)
        self.assertGreater(report['blockers'][0]['newly_activated_overlap_area'],0.)

    def test_obstruction_in_existing_native_overlap_alone_does_not_block_extension(self):
        native_only=row([(2.,2.),(4.,2.),(4.,4.),(2.,4.)])
        _,report=self.run_clear([native_only])
        self.assertEqual(report['state'],'clear_by_source_model_proxies')
        self.assertEqual(report['blockers'],[])

    def test_parked_traffic_and_accessible_stencil_do_not_block(self):
        traffic=row([(2.,12.),(4.,12.),(4.,14.),(2.,14.)],'occupancy')
        stencil=row([(6.,12.),(8.,12.),(8.,14.),(6.,14.)],'ground_marking')
        _,report=self.run_clear([traffic,stencil])
        self.assertEqual(report['state'],'clear_by_source_model_proxies')
        self.assertEqual(report['blockers'],[])

    def test_small_curbside_prop_insets_rectangle_within_limit_and_keeps_depth(self):
        prop=row([(2.,0.),(4.,0.),(4.,.5),(2.,.5)])
        with patch.object(obstacles,'nearby_models',return_value=[prop]):
            vertices,report=obstacles.clear_bank(None,BANK)
        self.assertEqual(report['state'],'clear_by_source_model_proxies')
        self.assertEqual(len(report['adjustments']),1)
        inset=report['adjustments'][0]['meters']
        self.assertLessEqual(inset,1.5)
        self.assertGreaterEqual(report['adjustments'][0]['remaining_depth'],20.)
        self.assertAlmostEqual(vertices[0][2],inset)

    def test_unclassified_model_blocks_instead_of_being_treated_as_absent(self):
        unknown=row([(2.,12.),(4.,12.),(4.,14.),(2.,14.)],'unknown_model')
        _,report=self.run_clear([unknown])
        self.assertEqual(report['state'],'blocked')
        self.assertEqual(report['blockers'][0]['class'],'unknown_model')

    def test_kind5_decoder_uses_diagonal_kdop_not_its_bounding_box(self):
        path='def/world/model.sii';name='/model/props/diagtest.pmd';model=token('diagtest')
        definition=f'SiiNunit {{\n model_def : model.diagtest {{\n  model_desc: "{name}"\n }}\n}}'
        # The axis-aligned box spans 1..3 on X/Z, but the KDOP diamond cuts away its corners.
        bounds=(1.,0.,1.,1.5,-.5,3.,1.,3.,2.5,.5)
        stack=MemoryStack({path:definition.encode(),SECTOR:model_sector(50,bounds,model)})
        candidate=[(1.,0.,1.),(1.2,0.,1.),(1.2,0.,1.2),(1.,0.,1.2)]
        rows=obstacles.nearby_models(stack,SECTOR,candidate)
        self.assertEqual(rows,[])
        # A footprint centered in the actual diagonal should decode the kind-5 model.
        inside=[(1.9,0.,1.9),(2.1,0.,1.9),(2.1,0.,2.1),(1.9,0.,2.1)]
        rows=obstacles.nearby_models(stack,SECTOR,inside)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['model_path'],name)
        self.assertEqual(rows[0]['class'],'static_model')

    def test_actual_kind5_neighbor_sector_is_discovered_but_outside_3x3_is_not(self):
        model=token('trashn');name='/model/props/trashn.pmd'
        definition=f'SiiNunit {{\n model_def : model.trashn {{\n model_desc: "{name}"\n }}\n}}'
        bounds=kdop(2.,4.,12.,14.)
        stack=MemoryStack({'def/world/model.sii':definition.encode(),
            SECTOR:struct.pack('<IQI',907,token('euro2'),3)+struct.pack('<I',0)+struct.pack('<I',0)+struct.pack('<I',0),
            NEIGHBOR:model_sector(51,bounds,model),OUTSIDE:model_sector(52,bounds,model)})
        rows=obstacles.nearby_models(stack,SECTOR,BANK['vertices'])
        self.assertEqual([r['sector'] for r in rows],[NEIGHBOR])
        self.assertEqual(rows[0]['model_path'],name)
        self.assertEqual(rows[0]['class'],'static_model')

    def test_actual_unknown_kind5_neighbor_blocks_new_space(self):
        unknown=token('unkprop')
        stack=MemoryStack({SECTOR:model_sector(60,kdop(2.,4.,12.,14.),unknown)})
        _,report=obstacles.clear_bank(stack,BANK,original_vertices=OLD)
        self.assertEqual(report['state'],'blocked')
        self.assertEqual(report['blockers'][0]['class'],'unknown_model')

if __name__=='__main__':unittest.main()
