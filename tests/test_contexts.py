#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Units(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.tree = namespace.parse_xmlns(self.instance_file)
        self.root = self.tree.getroot()

    def test_clean_contexts(self):
        expected_unused_contexts = sorted([
            "D2012Q2",
            "D2012Q1_CostOfSalesMember",
            "D2013Q1_CommonClassAMember",
            "D2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlow" \
                "HedgesMember",
            "I2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlow" \
                "HedgesMember"
        ])
        unused_contexts = sorted(xbrl.clean_contexts(self.root))

        self.assertEqual(unused_contexts, expected_unused_contexts)

        context_xpath = ".//{http://www.xbrl.org/2003/instance}context"
        context_ids = []
        contexts = self.root.findall(context_xpath)
        for context in contexts:
            context_ids.append(context.get("id"))

        for context in expected_unused_contexts:
            self.assertNotIn(context, context_ids)
