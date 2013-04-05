#!/usr/bin/env python

import unittest
from thinX import xbrl


class Units(unittest.TestCase):

	def test_get_units(self):
		unit_config_file = "test_units.ini"
		units_dictionary = xbrl.get_units(unit_config_file)

		self.assertIn("TestMeasures", units_dictionary)
		self.assertIn("TestMeasures2", units_dictionary)

		testMeasures = units_dictionary["TestMeasures"]

		self.assertEqual(testMeasures["Prefix"], "test")
		self.assertEqual(testMeasures["Namespace"],
		                 			  "http://www.example.org/1989/instance")
		self.assertEqual(testMeasures["Measures"], ["M1", "M2", "M3"])

	def test_add_namespace(self):
		pass

	def test_extended_measures(self):
		pass