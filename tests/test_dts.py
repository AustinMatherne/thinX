#!/usr/bin/env python

import unittest
from lxml import etree
from thinX import xbrl


class Dts(unittest.TestCase):

    def setUp(self):
        self.filename = "tests/assets/abc-20130331.xml"

    def test_open_linkbases(self):
        files = ["xsd", "pre", "def", "cal", "lab"]
        pre_name = "abc-20130331_pre.xml"
        fake_filename = "xyz-20130331.xml"
        result = xbrl.open_linkbases(self.filename, files)

        for linkbase in result:
            self.assertIn(linkbase, files)
        self.assertEqual(len(result), 5)
        self.assertTrue(etree.iselement(result["pre"]["root"]))
        self.assertEqual(result["pre"]["filename"].split("/")[-1], pre_name)
        self.assertRaises(OSError, xbrl.open_linkbases, fake_filename, files)
