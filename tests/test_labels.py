#!/usr/bin/env python

import unittest
from decimal import Decimal
from lxml import etree
from thinX import xbrl


class Labels(unittest.TestCase):

    def setUp(self):
        instance_file = "tests/assets/abc-20130331.xml"
        pre_linkbase = xbrl.get_linkbase(instance_file, "pre")
        lab_linkbase = xbrl.get_linkbase(instance_file, "lab")
        cal_linkbase = xbrl.get_linkbase(instance_file, "cal")
        tree = etree.parse(instance_file)
        pre_tree = etree.parse(pre_linkbase)
        lab_tree = etree.parse(lab_linkbase)
        cal_tree = etree.parse(cal_linkbase)
        self.root = tree.getroot()
        self.pre_root = pre_tree.getroot()
        self.lab_root = lab_tree.getroot()
        self.cal_root = cal_tree.getroot()
        self.standard_label = "http://www.xbrl.org/2003/role/label"
        self.terse_label = "http://www.xbrl.org/2003/role/terseLabel"
        self.verbose_label = "http://www.xbrl.org/2003/role/verboseLabel"
        self.negated_label = "http://www.xbrl.org/2009/role/negatedLabel"
        self.negated_terse_label = "http://www.xbrl.org/2009/role/negated" \
                                   "TerseLabel"

    def test_get_labels(self):
        found_labels = xbrl.get_labels(self.lab_root)
        concepts_with_labels = len(found_labels)
        expected = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                   "us-gaap-2012-01-31.xsd#us-gaap_StatementClassOfStockAxis"
        expected_labels = len(found_labels[expected])

        exp_terse_label = "Class of Stock [Axis]"

        self.assertEqual(236, concepts_with_labels)
        self.assertIn(expected, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertIn(self.terse_label, found_labels[expected])
        self.assertEqual(
            exp_terse_label,
            found_labels[expected][self.terse_label]
        )

    def test_get_used_labels(self):
        found_labels = xbrl.get_used_labels(self.pre_root)
        concepts_using_labels = len(found_labels)
        expected = "abc-20130331.xsd#abc_XYZHoldingsIncMember"
        expected_labels = len(found_labels[expected])

        self.assertEqual(234, concepts_using_labels)
        self.assertIn(expected, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertEqual(True, found_labels[expected][self.terse_label])

    def test_clean_labels(self):
        log = xbrl.clean_labels(self.lab_root, self.pre_root)
        concepts_with_deleted_labels = len(log)
        expected = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                   "us-gaap-2012-01-31.xsd#us-gaap_Goodwill"
        expected_labels = len(log[expected])
        period_start_label = "http://www.xbrl.org/2003/role/periodStartLabel"
        label = "Beginning Balance"

        self.assertEqual(19, concepts_with_deleted_labels)
        self.assertIn(expected, log)
        self.assertEqual(2, expected_labels)
        self.assertEqual(label, log[expected][period_start_label])

    def test_redundant_labels(self):
        log = xbrl.redundant_labels(self.lab_root, self.pre_root)
        concepts_with_redundant_labels = len(log)
        expected = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                   "us-gaap-2012-01-31.xsd#us-gaap_OtherComprehensive" \
                   "IncomeLossForeignCurrencyTransactionAnd" \
                   "TranslationAdjustmentNetOfTax"
        expected_pos_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                               "us-gaap-2012-01-31.xsd#us-gaap_Accumulated" \
                               "OtherComprehensiveIncomeLossNetOfTax"
        expected_neg_concept = "abc-20130331.xsd#abc_OutstandingBalanceUnder" \
                               "CommercialPaperProgram"
        expected_labels = len(log[expected])
        expected_pos_labels = len(log[expected_pos_concept])
        expected_neg_labels = len(log[expected_neg_concept])

        self.assertEqual(4, concepts_with_redundant_labels)
        self.assertIn(expected, log)
        self.assertIn(expected_pos_concept, log)
        self.assertIn(expected_neg_concept, log)
        self.assertEqual(1, expected_labels)
        self.assertEqual(8, expected_pos_labels)
        self.assertEqual(1, expected_neg_labels)
        self.assertNotIn(self.terse_label, log[expected])
        self.assertNotIn(self.terse_label, log[expected_pos_concept])
        self.assertNotIn(self.negated_label, log[expected_neg_concept])
        self.assertIn(self.verbose_label, log[expected])
        self.assertIn(self.verbose_label, log[expected_pos_concept])
        self.assertIn(self.negated_terse_label, log[expected_neg_concept])

    def test_remove_standard_labels(self):
        log = xbrl.remove_standard_labels(self.lab_root)
        base_concepts_with_standard_labels = len(log)
        expected = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                   "us-gaap-2012-01-31.xsd#us-gaap_" \
                   "InventoryWorkInProcessAndRawMaterialsNetOfReserves"
        expected_labels = len(log[expected])

        self.assertEqual(193, base_concepts_with_standard_labels)
        self.assertIn(expected, log)
        self.assertEqual(1, expected_labels)
        self.assertIn(self.standard_label, log[expected])

    def test_change_preferred_labels(self):
        expected = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                   "us-gaap-2012-01-31.xsd#us-gaap_MarketableSecurities" \
                   "RealizedGainLossExcludingOtherThanTemporaryImpairments"
        href_xpath = ".//*[@{http://www.w3.org/1999/xlink}href='%s']"
        to_attr_xpath = ".//*[@{http://www.w3.org/1999/xlink}to='%s']"
        label_attr = "{http://www.w3.org/1999/xlink}label"

        pre_elem = xbrl.change_preferred_labels(
            {expected: {self.negated_terse_label: self.negated_label}},
            self.pre_root
        )

        expected_locs = pre_elem.find(href_xpath % expected)
        label_ref = expected_locs.get(label_attr)
        arc = pre_elem.find(to_attr_xpath % label_ref)

        self.assertEqual(arc.get("preferredLabel"), self.negated_label)

    def test_insert_labels(self):
        calcs = xbrl.get_calcs(self.cal_root)
        log = xbrl.calc_values(self.root, calcs)
        label_log = xbrl.insert_labels(self.lab_root, log)
        debt = [
            "http://www.example.com/role/DebtLongTermDebtDetails",
            "Long-term Debt, Excluding Current Maturities",
            "us-gaap_LongTermDebtNoncurrent",
            "I2013Q1",
            Decimal("2989"),
            Decimal("11")
        ]
        self.assertIn(debt, label_log)
        self.assertEqual(len(label_log), 23)
