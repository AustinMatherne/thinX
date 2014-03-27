#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Labels(unittest.TestCase):

    def setUp(self):
        schema = "assets/abc-20130331.xsd"
        pre_linkbase = "assets/abc-20130331_pre.xml"
        def_linkbase = "assets/abc-20130331_def.xml"
        cal_linkbase = "assets/abc-20130331_cal.xml"
        xsd_tree = namespace.parse_xmlns(schema)
        pre_tree = namespace.parse_xmlns(pre_linkbase)
        def_tree = namespace.parse_xmlns(def_linkbase)
        cal_tree = namespace.parse_xmlns(cal_linkbase)
        self.xsd_root = xsd_tree.getroot()
        self.pre_root = pre_tree.getroot()
        self.def_root = def_tree.getroot()
        self.cal_root = cal_tree.getroot()

        self.active_link_roles = [
            "http://www.example.com/role/BalanceSheetComponents",
            "http://www.example.com/role/DocumentAndEntityInformation",
            "http://www.example.com/role/DebtTables",
            "http://www.example.com/role/DebtAdditionalInformationDetails"
        ]
        self.inactive_link_roles = [
            "http://www.example.com/role/InactiveDetails",
            "http://www.example.com/role/NotUsedDetails"
        ]

    def test_get_link_roles(self):
        result = xbrl.get_link_roles(self.xsd_root)

        for role in self.active_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 22)

    def test_get_active_link_roles(self):
        linkbases = {"pre": self.pre_root,
                     "def": self.def_root,
                     "cal": self.cal_root}

        result = xbrl.get_active_link_roles(linkbases)

        for role in self.active_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 20)

    def test_compare_link_roles(self):
        roles = xbrl.get_link_roles(self.xsd_root)
        active = xbrl.get_active_link_roles(linkbases)

        result = xbrl.compare_link_roles(roles, active)

        for role in self.inactive_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 2)
