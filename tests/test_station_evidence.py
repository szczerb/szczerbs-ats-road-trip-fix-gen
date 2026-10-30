"""Portable evidence preparation and public CLI/config boundary checks."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ats_road_trip.cli import main
from ats_road_trip.processors import ProcessorConfig
from ats_road_trip.station_parking.catalog import load_reviewed_catalog, reviewed_metadata
from ats_road_trip.station_parking.evidence import prepare_evidence


class StationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary=TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.converted=self.root/'converted';self.converted.mkdir()
        self.metadata=reviewed_metadata()
        for row in self.metadata['families']:
            for suffix,label in (('.pim','mesh'),('.pit','mesh_state')):
                text='Original project-authored fixture '+row['family']+suffix
                # Exercise a regular nested ConverterPIX output tree.
                path=self.converted/'prefab/gas'/(row['family']+suffix)
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
                row['fingerprints'][label]=hashlib.sha256(text.encode()).hexdigest()
        self.metadata_path=self.root/'metadata.json'
        self.metadata_path.write_text(json.dumps(self.metadata))
        self.output=self.root/'prepared'

    def prepare(self, **kwargs):
        return prepare_evidence([self.converted],self.output,metadata_path=self.metadata_path,**kwargs)

    def test_preparation_is_flat_portable_and_preserves_original_bytes(self):
        before={p.relative_to(self.converted):p.read_bytes() for p in self.converted.rglob('*') if p.is_file()}
        receipt=self.prepare()
        self.assertEqual(len(receipt['files']),8)
        self.assertEqual(len(list(self.output.iterdir())),9)
        self.assertFalse(receipt['redistribution_authorized'])
        self.assertEqual(len(load_reviewed_catalog(self.output,metadata_path=self.metadata_path)),4)
        for relative,data in before.items():
            self.assertEqual((self.converted/relative).read_bytes(),data)
            self.assertEqual((self.output/relative.name).read_bytes(),data)
        with self.assertRaisesRegex(FileExistsError,'already exists'):
            self.prepare()

    def test_missing_or_drifting_input_never_creates_output(self):
        path=next(self.converted.rglob('*.pit'));data=path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(ValueError,'Missing converted'):
            self.prepare()
        self.assertFalse(self.output.exists())
        path.write_text('wrong model state')
        with self.assertRaisesRegex(ValueError,'SHA-256 drift'):
            self.prepare()
        self.assertFalse(self.output.exists())
        path.write_bytes(data)

    def test_ambiguous_conversion_drift_is_rejected_even_if_one_file_matches(self):
        duplicate=self.converted/'other/nm_truckstop1_chemron.pim'
        duplicate.parent.mkdir();duplicate.write_text('drift')
        with self.assertRaisesRegex(ValueError,'SHA-256 drift'):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_config_normalizes_explicit_input_without_changing_legacy_defaults(self):
        config=ProcessorConfig.from_preset('realistic',station_evidence_dir=self.converted)
        self.assertEqual(config.station_evidence_dir,str(self.converted.resolve()))
        self.assertIsNone(ProcessorConfig.from_preset('broad').station_evidence_dir)
        for value in ('',[],False):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'directory path'):
                ProcessorConfig.from_preset('realistic',station_evidence_dir=value)

    def test_actual_workflows_fail_before_mounting_without_evidence(self):
        from ats_road_trip.bulk_run import generate_map_fix
        from ats_road_trip.map_stack import run_map_stack
        with patch('ats_road_trip.bulk_run._game_directory',side_effect=AssertionError('mounted')), \
             patch('ats_road_trip.map_stack._game_directory',side_effect=AssertionError('mounted')):
            with self.assertRaisesRegex(ValueError,'requires --station-evidence-dir'):
                generate_map_fix('original.scs',processors=['rest'],parking_strategy='station_bays')
            with self.assertRaisesRegex(ValueError,'requires --station-evidence-dir'):
                run_map_stack(packages=['original.scs'],preset='realistic')

    def test_cli_forwards_explicit_input_for_stack_and_single_map_analyze_generate(self):
        result={'status':'analyzed','report_path':'audit.json','workflow':{'work_dir':'work'},
                'planner':{'coverage':{'complete':True}},'outputs':[]}
        for command in ('analyze-map-stack','generate-map-stack','analyze-map','generate-map-fix'):
            stack=command.endswith('stack')
            target=('ats_road_trip.map_stack.run_map_stack' if stack else
                    'ats_road_trip.bulk_run.analyze_map' if command=='analyze-map' else
                    'ats_road_trip.bulk_run.generate_map_fix')
            args=([command,'--package','original.scs'] if stack else
                  [command,'original.scs','--processor','rest','--parking-strategy','station_bays'])
            args+=['--station-evidence-dir',str(self.converted)]
            if command.startswith('generate'):args+=['--experimental']
            with self.subTest(command=command),patch(target,return_value=result) as run, \
                 redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(main(args),0)
            self.assertEqual(run.call_args.kwargs['station_evidence_dir'],str(self.converted))
