#!/usr/bin/env python

import configparser
import collections


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
    prefix_end = prefix.split(":")[1]
    if prefix_end != "base":
        elem.set(prefix, ns)

    #Let's get some lowercase measures to work with.
    lower_clean_measures = [x.lower() for x in clean_measures]
    #And let's get rid of any duplicates.
    dup_measures = [x for x, y in collections.Counter(lower_clean_measures).items() if y > 1]
    #Store the xpath for retrieving measures.
    measure_xpath = ".//{http://www.xbrl.org/2003/instance}measure"
    #Find all measures.
    current_measures = elem.findall(measure_xpath)
    #For each measure.
    for element in current_measures:
        #Let's take the measure, minus the prefix.
        current_measure = element.text.split(":")[1]
        #For each clean measure.
        for clean_measure in clean_measures:
            clean_measure_lower = clean_measure.lower()
            if current_measure.lower() == clean_measure_lower:
                old = element.text
                if prefix_end == "base":
                    new = old.split(":")[0] + ":" + clean_measure
                else:
                    new = prefix_end + ":" + clean_measure
                if new != old:
                    if current_measure != clean_measure and clean_measure_lower in dup_measures:
                        pass
                    else:
                        element.text = new
                        log[old] = new

    return log

def extended_measures(elem, prefixes, ini):
    """Returns all extended measures in the supplied element."""
    log = []
    units = get_units(ini)
    base_units = units["BASE"]["Measures"]
    standard_prefixes = []
    for namespace in units:
        if units[namespace]["Prefix"] != "base":
            standard_prefixes.append(units[namespace]["Prefix"])
    all_prefixes = prefixes + standard_prefixes
    measure_xpath = ".//{http://www.xbrl.org/2003/instance}measure"
    current_measures = elem.findall(measure_xpath)
    for element in current_measures:
        current_prefix = element.text.split(":")[0]
        current_measure = element.text.split(":")[1]
        if current_prefix not in all_prefixes and current_measure not in base_units:
            if element.text not in log:
                log.append(element.text)

    return log

def clean_contexts(elem):
    """Search through the provided element's children for contexts. Find the
    ones which are not in use and remove them.

    """
    contexts = {}
    contexts_removed = []
    context_xpath = ".//{http://www.xbrl.org/2003/instance}context"
    current_contexts = elem.findall(context_xpath)
    for element in current_contexts:
        contexts[element] = element.get("id")
    for context in contexts:
        fact_values_xpath = ".//*[@contextRef='" + str(contexts[context]) + "']"
        fact_value = elem.find(fact_values_xpath)
        if fact_value is None:
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
    """Return all calculation relationships discovered in the given element."""
    store = {}
    calc_link_xpath = ".//{http://www.xbrl.org/2003/linkbase}calculationLink"
    calc_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}calculationArc"
    linkroles = elem.findall(calc_link_xpath)
    for linkrole in linkroles:
        link_role_href = linkrole.get("{http://www.w3.org/1999/xlink}role")
        store[link_role_href] = {}
        arcs = linkrole.findall(calc_arc_xpath)
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
    """Return all duplicate calculation relationships in the given element."""
    store = get_calcs(elem)
    warnings = {}

    def add_warning(total):
        #Check to see if a duplicate calculation has already been found.
        if total in warnings:
            warnings[total] += 1
        else:
            warnings[total] = 0

    base_calcs = {}
    #Loop through linkroles in store.
    for linkrole in store:
        #Loop through calculations in linkroles.
        for total in store[linkrole]:
            #Check if the total element is already in base_calcs.
            if total in base_calcs:
                #Check if the elements that add up to total are already found.
                new_children = set(store[linkrole][total])
                totals = base_calcs[total]
                if new_children in totals:
                    add_warning(total)
                else:
                    set_new_children = set(new_children)
                    found = False
                    for foot in totals:
                        set_old_children = set(foot)
                        if set_new_children.issubset(set_old_children):
                            add_warning(total)
                            found = True
                            break
                        elif set_new_children.issuperset(set_old_children):
                            add_warning(total)
                            foot = store[linkrole][total]
                            found = True
                            break

                    if not found:
                        totals.append(store[linkrole][total])

            #If the total element isn't already in base_calcs, add it.
            else:
                base_calcs[total] = [store[linkrole][total]]


    return warnings

