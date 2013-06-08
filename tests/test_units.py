#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Units(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.unit_config_file = "assets/units.ini"
        self.units_dictionary = xbrl.get_units(self.unit_config_file)
        self.tree = namespace.parse_xmlns(self.instance_file)
        self.root = self.tree.getroot()

    def test_get_units(self):
        self.assertIn("TestMeasures", self.units_dictionary)
        self.assertIn("TestMeasures2", self.units_dictionary)

        testMeasures = self.units_dictionary["TestMeasures"]

        self.assertEqual(testMeasures["Prefix"], "test")
        self.assertEqual(testMeasures["Namespace"],
                                      "http://www.example.org/1989/instance")
        self.assertEqual(testMeasures["Measures"], ["M1", "M2", "M3"])

    def test_add_namespace(self):
        prefix = "xmlns:test"
        ns = "http://www.example.org/1989/instance"
        measures = ["Y", "t", "T", "fake", "acre"]
        log = xbrl.add_namespace(self.root, prefix, ns, measures)

        self.assertEqual(self.root.get(prefix), ns)

        unit_elem = "{http://www.xbrl.org/2003/instance}unit[@id='%(unit)s']/*"

        year = self.root.findtext(unit_elem % {"unit": "Year"})
        tonne = self.root.findtext(unit_elem % {"unit": "Tonne"})
        ton = self.root.findtext(unit_elem % {"unit": "Ton"})
        acre = self.root.findtext(unit_elem % {"unit": "Acre"})

        self.assertEqual(year, "test:Y")
        self.assertEqual(tonne, "test:t")
        self.assertEqual(ton, "test:T")
        self.assertEqual(acre, "test:acre")

    def test_extended_measures(self):
        prefixes = ["xbrli", "iso4217"]
        extensions = ["abc:Y", "abc:acre", "abc:wk", "abc:MMcfe", "abc:MM",
                      "abc:mm", "abc:Q", "abc:t", "abc:T"]

        extended = xbrl.extended_measures(
            self.root,
            prefixes,
            self.unit_config_file
        )
        self.assertEqual(extended, extensions)
