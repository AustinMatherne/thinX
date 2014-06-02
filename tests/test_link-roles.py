#!/usr/bin/env python

import unittest
from lxml import etree
from thinX import xbrl


class Link_Roles(unittest.TestCase):

    def setUp(self):
        exts = [
            ("xsd", ".xsd"),
            ("pre", "_pre.xml"),
            ("def", "_def.xml"),
            ("cal", "_cal.xml")
        ]
        self.linkbases = {}
        for ext in exts:
            linkbase = self.linkbases[ext[0]] = {}
            linkbase["filename"] = "tests/assets/abc-20130331%s" % ext[1]
            linkbase["tree"] = etree.parse(linkbase["filename"])
            linkbase["root"] = linkbase["tree"].getroot()

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
        result = xbrl.get_link_roles(self.linkbases["xsd"]["root"])

        for role in self.active_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 22)

    def test_get_active_link_roles(self):
        result = xbrl.get_active_link_roles(self.linkbases)

        for role in self.active_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 20)

    def test_compare_link_roles(self):
        roles = xbrl.get_link_roles(self.linkbases["xsd"]["root"])
        active = xbrl.get_active_link_roles(self.linkbases)

        result = xbrl.compare_link_roles(roles, active)

        for role in self.inactive_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 2)

    def test_delete_link_roles(self):
        result = xbrl.delete_link_roles(self.linkbases["xsd"]["root"],
                                        self.inactive_link_roles)

        for role in self.inactive_link_roles:
            self.assertIn(role, result)
        self.assertEqual(len(result), 2)

    def test_link_role_def(self):
        role_uri = "http://www.example.com/role/NotUsedDetails"
        result = "4040 - Disclosure - Not Used (Details)"
        self.assertEqual(xbrl.link_role_def(self.linkbases["xsd"]["root"],
                                            role_uri), result)
