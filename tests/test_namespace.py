#!/usr/bin/env python

import unittest
from thinX import namespace


class Units(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.tree = namespace.parse_xmlns(self.instance_file)
        self.root = self.tree.getroot()
        self.elem = "OutstandingBalanceUnderRevolvingCreditFacility"
        self.url = "http://www.example.com/20130331"
        self.prefix = "abc"
        self.element_xpath = ".//{%(prefix)s}%(elem)s"
        self.exp_element = "us-gaap:" \
                           "AccumulatedOtherComprehensiveIncomeLossNetOfTax"
        self.child = self.root.find(
            ".//*[@contextRef='I2012_AccumulatedTranslationAdjustmentMember']"
        )
        self.uri_map = {
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

    def test_parse_xmlns(self):
        self.assertIn("xmlns:abc", self.root.attrib)
        self.assertIn("xmlns:us-gaap", self.root.attrib)
        self.assertIn("xmlns:xlink", self.root.attrib)
        self.assertEqual(8, len(self.root.attrib))

    def test_fixup_xmlns(self):
        namespace.fixup_xmlns(self.root)

        self.assertIsNotNone(self.root.find(
            "%(prefix)s:%(elem)s" % {"prefix": self.prefix, "elem": self.elem}
        ))
        self.assertIsNone(self.root.find(
            self.element_xpath % {"prefix": self.url, "elem": self.elem}
        ))

    def test_fixup_element_prefixes(self):
        namespace.fixup_element_prefixes(self.child, self.uri_map)

        self.assertEqual(self.child.tag, self.exp_element)
