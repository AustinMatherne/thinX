#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Units(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.unit_config_file = "assets/units.ini"
        self.units_dictionary = xbrl.get_units(self.unit_config_file)
        tree = namespace.parse_xmlns(self.instance_file)
        self.root = tree.getroot()

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
        base_prefix = "xmlns:abc"
        ns = "http://www.example.org/1989/instance"
        base_ns = "http://www.example.com/2013/base"
        measures = ["Y", "t", "T", "fake", "acre", "pure"]
        base_measures = ["item"]

        xbrl.add_namespace(self.root, prefix, ns, measures)
        xbrl.add_namespace(self.root, base_prefix, base_ns, base_measures)

        self.assertEqual(self.root.get(prefix), ns)

        unit_elem = "{http://www.xbrl.org/2003/instance}unit[@id='%(unit)s']/*"

        year = self.root.findtext(unit_elem % {"unit": "Year"})
        tonne = self.root.findtext(unit_elem % {"unit": "Tonne"})
        ton = self.root.findtext(unit_elem % {"unit": "Ton"})
        acre = self.root.findtext(unit_elem % {"unit": "Acre"})
        item = self.root.findtext(unit_elem % {"unit": "Item"})
        pure = self.root.findtext(unit_elem % {"unit": "Pure"})

        self.assertEqual(year, "test:Y")
        self.assertEqual(tonne, "test:t")
        self.assertEqual(ton, "test:T")
        self.assertEqual(acre, "test:acre")
        self.assertEqual(item, "abc:item")
        self.assertEqual(pure, "pure")

    def test_unknown_measures(self):
        expected_unknown = [
            "xbrli:shares", "iso4217:USD", "Pure", "iso4217:USD",
            "xbrli:shares", "abc:Item", "abc:fake", "abc:M1", "iso4217:typo",
            "abc:Y", "abc:acre", "abc:wk", "abc:MMcfe", "abc:MM", "abc:mm",
            "abc:Q", "abc:t", "abc:T"
        ]

        unknown = xbrl.unknown_measures(
            self.root,
            self.unit_config_file,
            self.instance_file
        )
        self.assertEqual(unknown, expected_unknown)
