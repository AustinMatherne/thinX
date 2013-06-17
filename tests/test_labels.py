#!/usr/bin/env python

import unittest
from thinX import namespace
from thinX import xbrl


class Labels(unittest.TestCase):

    def setUp(self):
        self.instance_file = "assets/abc-20130331.xml"
        self.tree = namespace.parse_xmlns(self.instance_file)
        self.root = self.tree.getroot()

    def test_get_labels(self):
        pass

    def test_get_used_labels(self):
        pass

    def test_clean_labels(self):
        pass
