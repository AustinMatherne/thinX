#!/usr/bin/env python

import configparser
import collections
from thinX import namespace


def get_file_namespace(filename):
    xsd = get_linkbase(filename, "xsd")
    tree = namespace.parse_xmlns(xsd)
    root = tree.getroot()
    name = root.get("targetNamespace")
    for item in root.items():
        if name in item and "targetNamespace" not in item:
            prefix = item[0].split(":")[1]
            break

    file_namespace = {"namespace": name, "prefix": prefix}
    return file_namespace

def get_units(ini, filename=False):
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


    if filename:
        file_namespace = get_file_namespace(filename)
        file_ns = file_namespace["namespace"]
        file_prefix = file_namespace["prefix"]
        registries["BASE"]["Namespace"] = file_ns
        registries["BASE"]["Prefix"] = file_prefix

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
    low_clean_measures = [x.lower() for x in clean_measures]
    #And let's get rid of any duplicates.
    low_clean_measures = [
        key
        for key, value in collections.Counter(low_clean_measures).items()
            if value > 1
    ]
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
            #Convert it to lowercase.
            clean_measure_lower = clean_measure.lower()
            #Compare it against the lowercase version of the current measure.
            if current_measure.lower() == clean_measure_lower:
                #Find the current measure, with prefix.
                old = element.text
                #Are we dealing with a base measure?
                if prefix_end == "base":
                    #If we are, save the clean measure with the old prefix.
                    new = old.split(":")[0] + ":" + clean_measure
                #If we aren't, save the clean measure with the new prefix.
                else:
                    new = prefix_end + ":" + clean_measure
                #If the clean measure is already set, don't bother writing it.
                if new != old:
                    #Are we dealing with a measure that's case sensitive?
                    if (
                        current_measure != clean_measure and
                        clean_measure_lower in low_clean_measures
                    ):
                        pass
                    #If not, set the clean measure.
                    else:
                        element.text = new
                        log[old] = new

    return log

def unknown_measures(elem, ini, filename):
    """Returns all measures in the supplied element which are not defined in the
    passed configuration file.

    """
    log = []
    prefixes = []
    units = get_units(ini, filename)
    measure_xpath = ".//{http://www.xbrl.org/2003/instance}measure"
    current_measures = elem.findall(measure_xpath)
    for element in current_measures:
        logit = True
        for item in units:
            prefix = units[item]["Prefix"]
            for measure in units[item]["Measures"]:
                if prefix + ":" + measure == element.text:
                    logit = False

        if logit:
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
        fact_values_xpath = ".//*[@contextRef='%s']" % str(contexts[context])
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
    calc_loc_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc"
    label_attr_xpath = "[@{http://www.w3.org/1999/xlink}label=\"%s\"]"
    linkroles = elem.findall(calc_link_xpath)
    for linkrole in linkroles:
        link_role_href = linkrole.get("{http://www.w3.org/1999/xlink}role")
        store[link_role_href] = {}
        arcs = linkrole.findall(calc_arc_xpath)
        for arc in arcs:
            arc_from = arc.get("{http://www.w3.org/1999/xlink}from")
            arc_to = arc.get("{http://www.w3.org/1999/xlink}to")
            label_from = linkrole.find(
                calc_loc_xpath + label_attr_xpath % arc_from
            )
            label_to = linkrole.find(
                calc_loc_xpath + label_attr_xpath % arc_to
            )
            parent = label_from.get("{http://www.w3.org/1999/xlink}href")
            child = label_to.get("{http://www.w3.org/1999/xlink}href")

            parent = parent.split("#")[1]
            child = child.split("#")[1]

            if parent not in store[link_role_href]:
                store[link_role_href][parent] = []
            store[link_role_href][parent].append(child)

    for linkrole in store:
        for parent in store[linkrole]:
            store[linkrole][parent].sort()
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
