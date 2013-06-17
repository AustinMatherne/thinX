#!/usr/bin/env python

import unittest
from thinX import namespace


class Namespace(unittest.TestCase):

    def setUp(self):
        instance_file = "assets/abc-20130331.xml"
        tree = namespace.parse_xmlns(instance_file)
        self.root = tree.getroot()

    def test_parse_xmlns(self):
        self.assertIn("xmlns:abc", self.root.attrib)
        self.assertIn("xmlns:us-gaap", self.root.attrib)
        self.assertIn("xmlns:xlink", self.root.attrib)
        self.assertEqual(9, len(self.root.attrib))

    def test_fixup_xmlns(self):
        element_xpath = ".//{%(prefix)s}%(elem)s"
        elem = "OutstandingBalanceUnderRevolvingCreditFacility"
        prefix = "abc"
        url = "http://www.example.com/20130331"
        namespace.fixup_xmlns(self.root)

        self.assertIsNotNone(self.root.find(
            "%(prefix)s:%(elem)s" % {"prefix": prefix, "elem": elem}
        ))
        self.assertIsNone(self.root.find(
            element_xpath % {"prefix": url, "elem": elem}
        ))

    def test_fixup_element_prefixes(self):
        exp_element = "us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax"
        uri_map = {
            'http://www.w3.org/1999/xlink': 'xlink',
            'http://www.xbrl.org/2003/instance': 'xbrli',
            'http://xbrl.org/2006/xbrldi': 'xbrldi',
            'http://www.xbrl.org/2003/iso4217': 'iso4217',
            'http://fasb.org/us-gaap/2012-01-31': 'us-gaap',
            'http://www.xbrl.org/2009/utr': 'utr',
            'http://xbrl.sec.gov/dei/2012-01-31': 'dei',
            'http://www.xbrl.org/2003/linkbase': 'link',
            'http://www.example.com/20130331': 'abc'
        }
        child = self.root.find(
            ".//*[@contextRef='I2012_AccumulatedTranslationAdjustmentMember']"
        )

        namespace.fixup_element_prefixes(child, uri_map)

        self.assertEqual(child.tag, exp_element)
