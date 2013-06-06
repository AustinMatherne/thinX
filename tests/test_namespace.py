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

    def test_parse_xmlns(self):
        self.assertIn("xmlns:abc", self.root.attrib)
        self.assertIn("xmlns:us-gaap", self.root.attrib)
        self.assertIn("xmlns:xlink", self.root.attrib)
        self.assertEqual(8, len(self.root.attrib))

    def test_fixup_element_prefixes(self):
        self.assertIsNone(self.root.find(
            self.element_xpath % {"prefix": self.prefix, "elem": self.elem}
        ))
        self.assertIsNotNone(self.root.find(
            self.element_xpath % {"prefix": self.url, "elem": self.elem}
        ))

    def test_fixup(self):
        pass

    def test_fixup_xmlns(self):
        pass
