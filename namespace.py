#!/usr/bin/env python

import xml.etree.ElementTree as ET


def parse_xmlns(file):
    """Opens the provided XML file and returns it as an ElementTree without
    throwing away its namespace prefix declarations.

    """
    events = "start", "start-ns"

    root = None
    ns_map = []

    # Parse the provided XML file and iterate over each element in the tree.
    for event, elem in ET.iterparse(file, events):

        # Append the elements namespace to ns_map.
        if event == "start-ns":
            ns_map.append(elem)

        # Add each namespace to the new document tree.
        elif event == "start":
            if root is None:
                root = elem
            for prefix, uri in ns_map:
                elem.set("xmlns:" + prefix, uri)
            ns_map = []

    # Return the document tree with namespace declarations.
    return ET.ElementTree(root)


def fixup_element_prefixes(elem, uri_map, memo={}):
    """Accepts an element and replaces any namespace it finds with its
    corresponding xmlns prefix.

    """
    def fixup(name):
        """Accepts an element name and if it finds a namespace, returns the
        element with the namespace replaced with its xmlns prefix. Otherwise,
        it returns nothing.

        """
        try:
            return memo[name]
        except KeyError:
            if name[0] != "{":
                return
            uri, tag = name[1:].split("}")
            if uri in uri_map:
                new_name = uri_map[uri] + ":" + tag
                memo[name] = new_name
                return new_name

    # Fix element name.
    name = fixup(elem.tag)
    if name:
        elem.tag = name

    # Fix attribute names.
    for key, value in elem.items():
        name = fixup(key)
        if name:
            elem.set(name, value)
            del elem.attrib[key]


def fixup_xmlns(elem, maps=None):
    """Accepts an element and iterates over its children, replacing any
    namespace it finds with its corresponding xmlns prefix.

    """
    if maps is None:
        maps = [{}]

    # Check for local overrides.
    xmlns = {}
    for key, value in elem.items():
        if key[:6] == "xmlns:":
            xmlns[value] = key[6:]
    if xmlns:
        uri_map = maps[-1].copy()
        uri_map.update(xmlns)
    else:
        uri_map = maps[-1]

    # Fixup this element.
    fixup_element_prefixes(elem, uri_map)

    # Process elements.
    maps.append(uri_map)
    for elem in elem:
        fixup_xmlns(elem, maps)
    maps.pop()
