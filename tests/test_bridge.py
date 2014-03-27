#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Calculations(unittest.TestCase):

    def setUp(self):
        schema = "assets/abc-20130331.xsd"
        pres = "assets/abc-20130331_pre.xml"
        defs = "assets/abc-20130331_def.xml"
        calc = "assets/abc-20130331_cal.xml"
        labs = "assets/abc-20130331_lab.xml"

        xsd_tree = namespace.parse_xmlns(schema)
        pre_tree = namespace.parse_xmlns(pres)
        def_tree = namespace.parse_xmlns(defs)
        cal_tree = namespace.parse_xmlns(calc)
        lab_tree = namespace.parse_xmlns(labs)

        self.xsd_root = xsd_tree.getroot()
        self.pre_root = pre_tree.getroot()
        self.def_root = def_tree.getroot()
        self.cal_root = cal_tree.getroot()
        self.lab_root = lab_tree.getroot()

    def test_link_role_sort(self):
        extps = [("0000", "00090"),
                 ("0025", "00205"),
                 ("3020", "30203"),
                 ("4012", "40103")]

        result = xbrl.link_role_sort(self.xsd_root)

        for expt in extps:
            self.assertIn(expt, result)
        self.assertEqual(len(result), 19)

    def test_rename_refs(self):
        files = [("abc-20130331.xsd", "abc-current_taxonomy.xsd"),
                 ("abc-20130331_pre.xml", "abc-current_taxonomy_pre.xml"),
                 ("abc-20130331_def.xml", "abc-current_taxonomy_def.xml"),
                 ("abc-20130331_cal.xml", "abc-current_taxonomy_cal.xml"),
                 ("abc-20130331_lab.xml", "abc-current_taxonomy_lab.xml"),
                 ("abc-20130331.xml", "*Deleted*")]

        result = xbrl.rename_refs(self.xsd_root, "xsd")

        for tup in files:
            self.assertIn(tup, result)
        self.assertEqual(len(result), 6)

    def test_remove_namespace_date(self):
        ns = ("http://www.example.com/20130331", "http://www.example.com")

        result = xbrl.remove_namespace_date(self.xsd_root)

        self.assertEqual(result, ns)
