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
                    if current_measure != clean_measure and clean_measure in ['m', 'mm', 't']:
                        pass
                    else:
                        element.text = new
                        log[old] = new

    return log

def extended_measures(elem, prefixes, ini):
    """..."""
    log = []
    units = get_units(ini)
    standard_prefixes = []
    for namespace in units:
        standard_prefixes.append(units[namespace]["Prefix"])
    all_prefixes = prefixes + standard_prefixes
    current_measures = elem.findall(".//{http://www.xbrl.org/2003/instance}measure")
    for element in current_measures:
        current_measure = element.text.split(":")[0]
        if current_measure not in all_prefixes:
            if element.text not in log:
                log.append(element.text)

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
        fact_values = ".//*[@contextRef='" + str(contexts[context]) + "']"
        temp = elem.find(fact_values)
        if temp is None:
            contexts_removed.append(contexts[context])
            elem.remove(context)

    return contexts_removed

def get_linkbase(filename, linkbase):
    """Find the requested linkbase in the provided element's DTS."""
    if linkbase == "xsd":
        return filename[:-3] + "xsd"
    else:
        return filename[:-4] + "_" + linkbase + ".xml"

def get_calcs(elem):
    """..."""
    store = {}
    linkroles = elem.findall(".//{http://www.xbrl.org/2003/linkbase}calculationLink")
    for linkrole in linkroles:
        link_role_href = linkrole.get("{http://www.w3.org/1999/xlink}role")
        store[link_role_href] = {}
        arcs = linkrole.findall(".//{http://www.xbrl.org/2003/linkbase}calculationArc")
        for arc in arcs:
            arc_from = arc.get("{http://www.w3.org/1999/xlink}from")
            arc_to = arc.get("{http://www.w3.org/1999/xlink}to")
            if arc_from not in store[link_role_href]:
                store[link_role_href][arc_from] = []
            store[link_role_href][arc_from].append(arc_to)

    for linkrole in store:
        for arc_from in store[linkrole]:
            store[linkrole][arc_from].sort()

    return store

def dup_calcs(elem):
    """..."""
    store = get_calcs(elem)
    warnings = {}
    base_calcs = {}
    for linkrole in store:
        for total in store[linkrole]:
            if total in base_calcs:
                if store[linkrole][total] in base_calcs[total]:
                    if total in warnings:
                        warnings[total] += 1
                    else:
                        warnings[total] = 0
                else:
                    base_calcs[total].append(store[linkrole][total])
            else:
                base_calcs[total] = [store[linkrole][total]]

    return warnings