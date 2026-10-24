"""Public complete-stack commands preserve analysis and generation boundaries."""
from contextlib import redirect_stderr,redirect_stdout
import io
import json
import unittest
from unittest.mock import patch

from ats_road_trip.cli import main,parser


class MapStackCliTests(unittest.TestCase):
    def invoke(self,args,result=None):
        result=result or {'status':'analyzed','outputs':[],
            'report_path':'/authored/audit.json','workflow':{'work_dir':'/authored'},
            'planner':{'coverage':{'complete':True}}}
        stdout=io.StringIO()
        with patch('ats_road_trip.map_stack.run_map_stack',return_value=result) as run,redirect_stdout(stdout):
            code=main(args)
        return code,json.loads(stdout.getvalue()),run

    def test_analysis_defaults_realistic_and_never_enables_generation(self):
        code,output,run=self.invoke(['analyze-map-stack','--package','first.scs','--package','second.scs'])
        self.assertEqual(code,0)
        run.assert_called_once_with(packages=['first.scs','second.scs'],preset='realistic',
            game_dir=None,extractor=None,run_id=None,generate=False,experimental=False,revision=13,improve_existing_car_parking=False,improve_truck_parking=False)
        self.assertTrue(output['analysis_only'])
        self.assertEqual(output['generated_mod_count'],0)
        self.assertEqual(output['report_path'],'/authored/audit.json')
        self.assertEqual(output['work_dir'],'/authored')

    def test_analysis_forwards_broad_stack_order_and_runtime_flags(self):
        _,_,run=self.invoke(['--extractor','/tools/extractor','analyze-map-stack',
            '--package','low.scs','--package','high.scs','--preset','broad',
            '--game-dir','/games/ATS','--run-id','2026-10-21_20-57-43'])
        run.assert_called_once_with(packages=['low.scs','high.scs'],preset='broad',
            game_dir='/games/ATS',extractor='/tools/extractor',run_id='2026-10-21_20-57-43',
            generate=False,experimental=False,revision=13,improve_existing_car_parking=False,improve_truck_parking=False)

    def test_generation_requires_experimental_before_workflow_dispatch(self):
        stderr=io.StringIO()
        with patch('ats_road_trip.map_stack.run_map_stack') as run,redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(['generate-map-stack','--package','original.scs'])
        self.assertEqual(raised.exception.code,2)
        run.assert_not_called()
        self.assertIn('Generation requires --experimental',stderr.getvalue())

    def test_generation_forwards_revision_and_all_options(self):
        result={'status':'generated','outputs':[{'path':'/outputs/first.scs'},{'path':'/outputs/second.scs'}],
                'planner':{'coverage':{'complete':True}}}
        code,output,run=self.invoke(['--extractor','/tools/extractor','generate-map-stack',
            '--package','low.scs','--package','high.scs','--preset','realistic','--revision','12',
            '--game-dir','/games/ATS','--run-id','2026-10-21_20-57-43','--experimental'],result)
        self.assertEqual(code,0)
        run.assert_called_once_with(packages=['low.scs','high.scs'],preset='realistic',
            game_dir='/games/ATS',extractor='/tools/extractor',run_id='2026-10-21_20-57-43',
            generate=True,experimental=True,revision=12,improve_existing_car_parking=False,improve_truck_parking=False)
        self.assertFalse(output['analysis_only'])
        self.assertEqual(output['generated_mod_count'],2)
        self.assertEqual(output['outputs'],result['outputs'])

    def test_generation_revision_defaults_to_thirteen(self):
        _,_,run=self.invoke(['generate-map-stack','--package','original.scs','--experimental'])
        self.assertEqual(run.call_args.kwargs['revision'],13)
        self.assertTrue(run.call_args.kwargs['generate'])

    def test_native_improvement_flag_forwards_for_analysis_and_generation(self):
        for command in ('analyze-map-stack','generate-map-stack'):
            args=[command,'--package','source.scs','--improve-existing-car-parking']
            if command.startswith('generate'):args.append('--experimental')
            _,_,run=self.invoke(args)
            self.assertTrue(run.call_args.kwargs['improve_existing_car_parking'])

    def test_packages_required_and_preset_choices_are_strict(self):
        for args in (['analyze-map-stack'],['generate-map-stack','--experimental'],
                     ['analyze-map-stack','--package','original.scs','--preset','unknown']):
            with self.subTest(args=args),redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as raised:
                parser().parse_args(args)
            self.assertEqual(raised.exception.code,2)

    def test_analysis_rejects_generation_only_flags(self):
        for flag in ('--experimental','--revision'):
            args=['analyze-map-stack','--package','original.scs',flag]
            if flag=='--revision':args.append('11')
            with self.subTest(flag=flag),redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as raised:
                main(args)
            self.assertEqual(raised.exception.code,2)


if __name__=='__main__':unittest.main()
