#!/usr/bin/env python

import unittest
from lxml import etree
from thinX import xbrl


class Link_Roles(unittest.TestCase):

    def setUp(self):
        schema = "tests/assets/abc-20130331.xsd"
        pre_linkbase = "tests/assets/abc-20130331_pre.xml"
        def_linkbase = "tests/assets/abc-20130331_def.xml"
        cal_linkbase = "tests/assets/abc-20130331_cal.xml"
        xsd_tree = etree.parse(schema)
        pre_tree = etree.parse(pre_linkbase)
        def_tree = etree.parse(def_linkbase)
        cal_tree = etree.parse(cal_linkbase)
        self.xsd_root = xsd_tree.getroot()
        self.linkbases = {"pre": pre_tree.getroot(),
                          "def": def_tree.getroot(),
                          "cal": cal_tree.getroot()}

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
        result = xbrl.get_active_link_roles(self.linkbases)

        for role in self.active_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 20)

    def test_compare_link_roles(self):
        roles = xbrl.get_link_roles(self.xsd_root)
        active = xbrl.get_active_link_roles(self.linkbases)

        result = xbrl.compare_link_roles(roles, active)

        for role in self.inactive_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 2)

    def test_delete_link_roles(self):
        result = xbrl.delete_link_roles(self.xsd_root,
                                        self.inactive_link_roles)

        for role in self.inactive_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 2)

    def test_link_role_def(self):
        role_uri = "http://www.example.com/role/NotUsedDetails"
        result = "4040 - Disclosure - Not Used (Details)"
        self.assertEqual(xbrl.link_role_def(self.xsd_root, role_uri), result)
