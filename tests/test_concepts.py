#!/usr/bin/env python

import unittest
from lxml import etree
from thinX import xbrl


class Concepts(unittest.TestCase):

    def setUp(self):
        instance_file = "tests/assets/abc-20130331.xml"
        files = ["xsd", "pre", "def", "cal", "lab"]
        self.linkbases = xbrl.open_linkbases(instance_file, files)

    def test_clean_concepts(self):
        expected_concept = "abc_RemoveMe"

        removed_concepts = xbrl.clean_concepts(self.linkbases)

        concepts_without_references = len(removed_concepts)

        self.assertEqual(2, concepts_without_references)
        self.assertIn(expected_concept, removed_concepts)
