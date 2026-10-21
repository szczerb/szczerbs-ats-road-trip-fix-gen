import unittest
from ats_road_trip.processors import ProcessorConfig,Processor,ParkingStrategy,CompatibilityPreset
from ats_road_trip.fuel_selection import FuelSelectionConfig

class RealisticPresetTests(unittest.TestCase):
    def test_existing_selection_keeps_truck_parking_and_broad_fuel(self):
        c=ProcessorConfig.from_names(['fuel','rest'])
        self.assertEqual(c.parking_strategy,ParkingStrategy.TRUCK_AREAS)
        self.assertEqual(c.fuel_selection,FuelSelectionConfig())
        self.assertEqual(ProcessorConfig().parking_strategy,ParkingStrategy.NONE)
    def test_realistic_defaults_and_independent_configuration(self):
        c=ProcessorConfig.from_preset('realistic')
        self.assertEqual(c.fuel_selection.classifier,'facilities')
        self.assertEqual(c.fuel_selection.unknown,'include')
        self.assertEqual(c.parking_strategy,ParkingStrategy.STATION_BAYS)
        self.assertEqual(c.enabled,(Processor.FUEL,Processor.REST))
        c=ProcessorConfig.from_preset('realistic',fuel_selection=FuelSelectionConfig())
        self.assertEqual(c.fuel_selection.mode,'broad')
        self.assertEqual(c.parking_strategy,ParkingStrategy.STATION_BAYS)
        self.assertEqual(ProcessorConfig.from_preset('broad').parking_strategy,ParkingStrategy.TRUCK_AREAS)
        self.assertEqual(ProcessorConfig.from_preset('realistic',enabled=['fuel']).parking_strategy,ParkingStrategy.NONE)
        c=ProcessorConfig.from_preset('realistic',enabled=['rest'])
        self.assertEqual(c.parking_strategy,ParkingStrategy.STATION_BAYS)
        self.assertEqual(c.fuel_selection,FuelSelectionConfig())
    def test_impossible_combinations_fail(self):
        for kwargs in ({'parking_strategy':'station_bays'},
                       {'enabled':(Processor.REST,),'parking_strategy':'none'},
                       {'enabled':(Processor.REST,),'parking_strategy':('truck_areas','station_bays')}):
            with self.assertRaises(ValueError):ProcessorConfig(**kwargs)
        with self.assertRaises(ValueError):ProcessorConfig.from_preset('imaginary')
