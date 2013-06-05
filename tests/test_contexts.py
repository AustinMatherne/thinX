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
        expected_unused_contexts = [
            "D2012Q1_CostOfSalesMember",
            "D2012Q2",
            "D2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlowHedgesMember",
            "D2013Q1_CommonClassAMember",
            "I2012Q2_AccumulatedNetGainLossFromDesignatedOrQualifyingCashFlowHedgesMember"
        ]
        log = sorted(xbrl.clean_contexts(self.root))

        self.assertEqual(log, expected_unused_contexts)
        mine = []
        temps = self.root.findall(".//{http://www.xbrl.org/2003/instance}context")
        for temp in temps:
            mine.append(temp.get("id"))

        for context in expected_unused_contexts:
            self.assertNotIn(context, mine, msg=mine)
