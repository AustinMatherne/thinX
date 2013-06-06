#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Units(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.tree = namespace.parse_xmlns(self.instance_file)
        self.root = self.tree.getroot()

    def test_get_linkbase(self):
        schema = xbrl.get_linkbase(self.instance_file, "xsd")
        pre_linkbase = xbrl.get_linkbase(self.instance_file, "pre")
        def_linkbase = xbrl.get_linkbase(self.instance_file, "def")
        cal_linkbase = xbrl.get_linkbase(self.instance_file, "cal")
        lab_linkbase = xbrl.get_linkbase(self.instance_file, "lab")

        self.assertEqual(schema, "assets/abc-20130331.xsd")
        self.assertEqual(pre_linkbase, "assets/abc-20130331_pre.xml")
        self.assertEqual(def_linkbase, "assets/abc-20130331_def.xml")
        self.assertEqual(cal_linkbase, "assets/abc-20130331_cal.xml")
        self.assertEqual(lab_linkbase, "assets/abc-20130331_lab.xml")

    def test_get_calcs(self):
        pass

    def test_dup_calcs(self):
        pass
