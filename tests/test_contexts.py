#!/usr/bin/env python

import unittest
from lxml import etree
from thinX import xbrl


class Contexts(unittest.TestCase):

    def setUp(self):
        instance_file = "tests/assets/abc-20130331.xml"
        tree = etree.parse(instance_file)
        self.root = tree.getroot()

    def test_clean_contexts(self):
        expected_unused_contexts = sorted([
            "D2012Q2",
            "D2012Q1_CostOfSalesMember",
            "D2013Q1_CommonClassAMember",
            "D2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlow"
            "HedgesMember",
            "I2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlow"
            "HedgesMember",
            "D2012Q2_M0630",
            "D2013Q1_M0201_CostOfSalesMember",
            "D2012Q1_M0101"
        ])
        unused_contexts = sorted(xbrl.clean_contexts(self.root))

        self.assertEqual(unused_contexts, expected_unused_contexts)

        context_xpath = ".//{http://www.xbrl.org/2003/instance}context"
        contexts = self.root.findall(context_xpath)
        context_ids = []
        for context in contexts:
            context_ids.append(context.get("id"))

        for context in expected_unused_contexts:
            self.assertNotIn(context, context_ids)

    def test_two_day_contexts(self):
        two_day_contexts = ["D2012Q2_M0630",
                            "D2013Q1_M0201_CostOfSalesMember",
                            "D2012Q1_M0101"]

        result = xbrl.two_day_contexts(self.root)

        for context in two_day_contexts:
            self.assertIn(context, result)
        self.assertEqual(len(result), 3)
