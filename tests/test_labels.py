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

    def test_get_labels(self):
        found_labels = xbrl.get_labels(self.lab_root)
        concepts_with_labels = len(found_labels)
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_StatementClassOf" \
                           "StockAxis"
        expected_labels = len(found_labels[expected_concept])
        terse_label = "http://www.xbrl.org/2003/role/terseLabel"
        exp_terse_label = "Class of Stock [Axis]"

        self.assertEqual(236, concepts_with_labels)
        self.assertIn(expected_concept, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertIn(terse_label, found_labels[expected_concept])
        self.assertEqual(
            exp_terse_label,
            found_labels[expected_concept][terse_label]
        )

    def test_get_used_labels(self):
        found_labels = xbrl.get_used_labels(self.pre_root)
        concepts_using_labels = len(found_labels)
        expected_concept = "abc-20130331.xsd#abc_XYZHoldingsIncMember"
        expected_labels = len(found_labels[expected_concept])
        terse_label = "http://www.xbrl.org/2003/role/terseLabel"

        self.assertEqual(235, concepts_using_labels)
        self.assertIn(expected_concept, found_labels)
        self.assertEqual(2, expected_labels)
        self.assertEqual(True, found_labels[expected_concept][terse_label])

    def test_clean_labels(self):
        log = xbrl.clean_labels(self.lab_root, self.pre_root)
        concepts_with_deleted_labels = len(log)
        expected_concept = "http://xbrl.fasb.org/us-gaap/2012/elts/" \
                           "us-gaap-2012-01-31.xsd#us-gaap_Goodwill"
        expected_labels = len(log[expected_concept])
        period_start_label = "http://www.xbrl.org/2003/role/periodStartLabel"
        label = "Beginning Balance"

        self.assertEqual(17, concepts_with_deleted_labels)
        self.assertIn(expected_concept, log)
        self.assertEqual(2, expected_labels)
        self.assertEqual(label, log[expected_concept][period_start_label])

