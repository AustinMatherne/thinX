#!/usr/bin/env python

import configparser


def get_units(ini):
    """Parses the supplied configuration file for unit namespaces, prefixes,
    and measures.

    """
    config = configparser.ConfigParser()
    config.read(ini)
    sections = config.sections()
    registries = {}
    for section in sections:
        registries[section] = {}
        prefix = config[section]["Prefix"]
        registries[section]["Prefix"] = prefix
        namespace = config[section]["Namespace"]
        registries[section]["Namespace"] = namespace
        measures = config[section]["Measures"].split(",")
        clean_measures = []
        for measure in measures:
            clean_measures.append(measure.lstrip('\n'))
        registries[section]["Measures"] = clean_measures

    # Return a dictionary containing a dictionary for each namespace, which
    # contains a prefix, namespace, and a list of measures.
    return registries


def add_namespace(elem, prefix, ns, clean_measures):
    """Accepts an element, a prefix, a namespace, and a list of measures.
    Declares the namespace and prefix in the provided element, then searches
    through the element's children for declared units of measure. For each
    measure that is found, it executes a case insensitive search against the
    supplied list of measures for a match, if a match is found, the measure
    and its prefix are replaced with the provided prefix and clean measure.

    """
    log = {}
    elem.set(prefix, ns)
    current_measures = elem.findall(".//{http://www.xbrl.org/2003/instance}measure")
    for element in current_measures:
        current_measure = element.text.split(":")[1]
        for clean_measure in clean_measures:
            if current_measure.lower() == clean_measure.lower():
                old = element.text
                new = prefix.split(":")[1] + ":" + clean_measure
                if new != old:
                    element.text = new
                    log[old] = new
    return log


def clean_contexts(elem):
    """Search through the provided element's children for contexts. Find the
    ones which are not in use and remove them.

    """
    contexts = {}
    contexts_removed = []
    current_contexts = elem.findall(".//{http://www.xbrl.org/2003/instance}context")
    for element in current_contexts:
        contexts[element] = element.get("id")
    for context in contexts:
        wtf = ".//*[@contextRef='" + str(contexts[context]) + "']"
        temp = elem.find(wtf)
        if temp is None:
            contexts_removed.append(contexts[context])
            elem.remove(context)

    return contexts_removed
