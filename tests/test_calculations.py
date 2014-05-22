#!/usr/bin/env python

import unittest
from decimal import Decimal
from thinX import namespace
from thinX import xbrl


class Calculations(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        cal_linkbase = xbrl.get_linkbase(self.instance_file, "cal")
        tree = namespace.parse_xmlns(self.instance_file)
        cal_tree = namespace.parse_xmlns(cal_linkbase)
        self.root = tree.getroot()
        self.cal_root = cal_tree.getroot()

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
        linkrole = "http://www.example.com/role/BalanceSheetComponents" \
                        "InventoriesDetails"
        total = "us-gaap_InventoryNet"
        elems_to_add = [
            ("us-gaap_InventoryFinishedGoodsNetOfReserves", "1"),
            ("us-gaap_InventoryWorkInProcessAndRawMaterialsNetOfReserves", "1")
        ]

        calc_linkroles = xbrl.get_calcs(self.cal_root)
        total_elements = []
        for calc_linkrole in calc_linkroles:
            for calc_total in calc_linkroles[calc_linkrole]:
                total_elements.append(calc_total)

        self.assertEqual(11, len(calc_linkroles))
        self.assertIn(total, calc_linkroles[linkrole])
        self.assertEqual(32, len(total_elements))
        self.assertEqual(elems_to_add, calc_linkroles[linkrole][total])

    def test_dup_calcs(self):
        expected_dup_calcs = {
            "us-gaap_OtherComprehensiveIncomeLossAvailableForSaleSecurities" \
            "AdjustmentNetOfTax": 0,
            "us-gaap_NetCashProvidedByUsedInInvestingActivities": 1,
            "us-gaap_NetIncomeLoss": 0
        }
        duplicate_calcs = xbrl.dup_calcs(self.cal_root)

        self.assertEqual(expected_dup_calcs, duplicate_calcs)

    def test_calc_values(self):
        debts = [[
            "http://www.example.com/role/DebtLongTermDebtDetails",
            "us-gaap_LongTermDebtNoncurrent",
            "I2013Q1",
            Decimal("2989"),
            Decimal("11")
        ], [
            "http://www.example.com/role/DebtAdditionalInformationDetails",
            "us-gaap_DebtWeightedAverageInterestRate",
            "I2013Q1",
            Decimal("0.9843"),
            Decimal("0.05734")
        ]]

        calcs = xbrl.get_calcs(self.cal_root)
        log = xbrl.calc_values(self.root, calcs)
        for debt in debts:
            self.assertIn(debt, log)
        self.assertEqual(len(log), 23)
