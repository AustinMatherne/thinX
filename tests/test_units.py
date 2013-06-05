#!/usr/bin/env python

import unittest
from thinX import xbrl


class Units(unittest.TestCase):

    def setUp(self):
        self.unit_config_file = "assets/units.ini"
        self.units_dictionary = xbrl.get_units(self.unit_config_file)

    def test_get_units(self):
        self.assertIn("TestMeasures", self.units_dictionary)
        self.assertIn("TestMeasures2", self.units_dictionary)

        testMeasures = self.units_dictionary["TestMeasures"]

        self.assertEqual(testMeasures["Prefix"], "test")
        self.assertEqual(testMeasures["Namespace"],
                                      "http://www.example.org/1989/instance")
        self.assertEqual(testMeasures["Measures"], ["M1", "M2", "M3"])

    def test_add_namespace(self):
        pass

    def test_extended_measures(self):
        pass