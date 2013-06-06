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

        self.assertEqual("assets/abc-20130331.xsd", schema)
        self.assertEqual("assets/abc-20130331_pre.xml", pre_linkbase)
        self.assertEqual("assets/abc-20130331_def.xml", def_linkbase)
        self.assertEqual("assets/abc-20130331_cal.xml", cal_linkbase)
        self.assertEqual("assets/abc-20130331_lab.xml", lab_linkbase)

    def test_get_calcs(self):
        cal_linkbase = xbrl.get_linkbase(self.instance_file, "cal")
        cal_tree = namespace.parse_xmlns(cal_linkbase)
        cal_root = cal_tree.getroot()
        linkrole = "http://www.example.com/role/BalanceSheetComponents" \
                        "InventoriesDetails"
        total = "InventoryNet"
        elems_to_add = sorted([
            "InventoryWorkInProcessAndRawMaterialsNetOfReserves",
            "InventoryFinishedGoodsNetOfReserves"
        ])

        calc_linkroles = xbrl.get_calcs(cal_root)
        total_elements = []
        for calc_linkrole in calc_linkroles:
            for calc_total in calc_linkroles[calc_linkrole]:
                total_elements.append(calc_total)

        #Check for the correct amount of linkroles.
        self.assertEqual(10, len(calc_linkroles))
        #Check that the total element is in the linkrole.
        self.assertIn(total, calc_linkroles[linkrole])
        #Check for the correct amount of total elements.
        self.assertEqual(31, len(total_elements))
        #Check that the elements that add to the total element are in the list.
        self.assertEqual(elems_to_add, calc_linkroles[linkrole][total])

    def test_dup_calcs(self):
        cal_linkbase = xbrl.get_linkbase(self.instance_file, "cal")
        cal_tree = namespace.parse_xmlns(cal_linkbase)
        cal_root = cal_tree.getroot()
        expected_dup_calcs = {
            "OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax": 0,
            "NetCashProvidedByUsedInInvestingActivities": 1
        }
        duplicate_calcs = xbrl.dup_calcs(cal_root)

        self.assertEqual(expected_dup_calcs, duplicate_calcs)
