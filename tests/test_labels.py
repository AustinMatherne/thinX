#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Labels(unittest.TestCase):

    def setUp(self):
        instance_file = "assets/abc-20130331.xml"
        pre_linkbase = xbrl.get_linkbase(instance_file, "pre")
        lab_linkbase = xbrl.get_linkbase(instance_file, "lab")
        pre_tree = namespace.parse_xmlns(pre_linkbase)
        lab_tree = namespace.parse_xmlns(lab_linkbase)
        self.pre_root = pre_tree.getroot()
        self.lab_root = lab_tree.getroot()
        self.terse_label = "http://www.xbrl.org/2003/role/terseLabel"
        self.verbose_label = "http://www.xbrl.org/2003/role/verboseLabel"
        self.negated_label = "http://www.xbrl.org/2009/role/negatedLabel"
        self.negated_terse_label = "http://www.xbrl.org/2009/role/negated" \
                                   "TerseLabel"

    def test_get_labels(self):
        found_labels = xbrl.get_labels(self.lab_root)
        concepts_with_labels = len(found_labels)
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_StatementClassOf" \
                           "StockAxis"
        expected_labels = len(found_labels[expected_concept])

        exp_terse_label = "Class of Stock [Axis]"

        self.assertEqual(235, concepts_with_labels)
        self.assertIn(expected_concept, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertIn(self.terse_label, found_labels[expected_concept])
        self.assertEqual(
            exp_terse_label,
            found_labels[expected_concept][self.terse_label]
        )

    def test_get_used_labels(self):
        found_labels = xbrl.get_used_labels(self.pre_root)
        concepts_using_labels = len(found_labels)
        expected_concept = "abc-20130331.xsd#abc_XYZHoldingsIncMember"
        expected_labels = len(found_labels[expected_concept])

        self.assertEqual(233, concepts_using_labels)
        self.assertIn(expected_concept, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertEqual(True, found_labels[expected_concept][self.terse_label])

    def test_clean_labels(self):
        log = xbrl.clean_labels(self.lab_root, self.pre_root)
        concepts_with_deleted_labels = len(log)
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_Goodwill"
        expected_labels = len(log[expected_concept])
        period_start_label = "http://www.xbrl.org/2003/role/periodStartLabel"
        label = "Beginning Balance"

        self.assertEqual(19, concepts_with_deleted_labels)
        self.assertIn(expected_concept, log)
        self.assertEqual(2, expected_labels)
        self.assertEqual(label, log[expected_concept][period_start_label])

    def test_redundant_labels(self):
        log = xbrl.redundant_labels(self.lab_root, self.pre_root)
        concepts_with_redundant_labels = len(log)
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_OtherComprehensive" \
                           "IncomeLossForeignCurrencyTransactionAnd" \
                           "TranslationAdjustmentNetOfTax"
        expected_pos_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_AccumulatedOther" \
                           "ComprehensiveIncomeLossNetOfTax"
        expected_neg_concept = "abc-20130331.xsd#abc_OutstandingBalanceUnder" \
                               "CommercialPaperProgram"
        expected_labels = len(log[expected_concept])
        expected_pos_labels = len(log[expected_pos_concept])
        expected_neg_labels = len(log[expected_neg_concept])

        self.assertEqual(4, concepts_with_redundant_labels)
        self.assertIn(expected_concept, log)
        self.assertIn(expected_pos_concept, log)
        self.assertIn(expected_neg_concept, log)
        self.assertEqual(1, expected_labels)
        self.assertEqual(8, expected_pos_labels)
        self.assertEqual(1, expected_neg_labels)
        self.assertNotIn(self.terse_label, log[expected_concept])
        self.assertNotIn(self.terse_label, log[expected_pos_concept])
        self.assertNotIn(self.negated_label, log[expected_neg_concept])
        self.assertIn(self.verbose_label, log[expected_concept])
        self.assertIn(self.verbose_label, log[expected_pos_concept])
        self.assertIn(self.negated_terse_label, log[expected_neg_concept])

    def test_change_preferred_label(self):
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_Marketable" \
                           "SecuritiesRealizedGainLossExcludingOtherThan" \
                           "TemporaryImpairments"
        href_xpath = ".//*[@{http://www.w3.org/1999/xlink}href='%s']"
        to_attr_xpath = ".//*[@{http://www.w3.org/1999/xlink}to='%s']"
        label_attr = "{http://www.w3.org/1999/xlink}label"

        pre_elem = xbrl.change_preferred_label(
            expected_concept,
            self.pre_root,
            self.negated_terse_label,
            self.negated_label
        )

        expected_concept_locs = pre_elem.find(href_xpath % expected_concept)
        label_ref = expected_concept_locs.get(label_attr)
        arc = pre_elem.find(to_attr_xpath % label_ref)

        self.assertEqual(arc.get("preferredLabel"), self.negated_label)
