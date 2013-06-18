#!/usr/bin/env python

import configparser
import collections
import re
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
        current_measure = element.text.split(":")
        if len(current_measure) > 1:
            noprefix = False
            current_measure = current_measure[1]
        else:
            noprefix = True
            current_measure = current_measure[0]
        #For each clean measure.
        for clean_measure in clean_measures:
            #Convert it to lowercase.
            clean_measure_lower = clean_measure.lower()
            #Compare it against the lowercase version of the current measure.
            if current_measure.lower() == clean_measure_lower:
                #Find the current measure, with, or without prefix.
                old = element.text
                #Check to see if we were using a prefix.
                if noprefix:
                    #We weren't, so save the clean measure without a prefix.
                    new = clean_measure
                else:
                    #We were, so save the clean measure with the new prefix.
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
    units = get_units(ini, filename)
    measure_xpath = ".//{http://www.xbrl.org/2003/instance}measure"
    current_measures = elem.findall(measure_xpath)
    for element in current_measures:
        logit = True
        for namespace, unit_set in units.items():
            prefix = unit_set["Prefix"]
            for measure in unit_set["Measures"]:
                if len(element.text.split(":")) > 1:
                    if prefix + ":" + measure == element.text:
                        logit = False
                else:
                    if measure == element.text:
                        logit = False

        if logit:
            log.append(element.text)

    return log

def get_labels(lab_elem):
    """Return a dictionary of all labels in the element."""
    found_labels = {}
    loc_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc"
    label_xpath = ".//{http://www.xbrl.org/2003/linkbase}label" \
                  "[@{http://www.w3.org/1999/xlink}label=\"%s\"]"
    label_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelArc" \
                      "[@{http://www.w3.org/1999/xlink}from=\"%s\"]"
    role_attr_xpath = "{http://www.w3.org/1999/xlink}role"
    to_attr_xpath = "{http://www.w3.org/1999/xlink}to"
    href_attr_xpath = "{http://www.w3.org/1999/xlink}href"
    label_attr_xpath = "{http://www.w3.org/1999/xlink}label"
    locs = lab_elem.findall(loc_xpath)

    for loc in locs:
        concept = loc.get(href_attr_xpath)
        concept_label = loc.get(label_attr_xpath)
        if concept not in found_labels:
            found_labels[concept] = {}
        label_arcs = lab_elem.findall(label_arc_xpath % concept_label)
        for label_arc in label_arcs:
            element = label_arc.get(to_attr_xpath)
            label_element = lab_elem.find(label_xpath % element)
            label_type = label_element.get(role_attr_xpath)
            label = label_element.text
            found_labels[concept][label_type] = label

    return found_labels

def get_used_labels(pre_elem):
    """Return a dictionary listing all active labels in the element."""
    found_labels = {}
    loc_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc"
    pre_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}presentationArc" \
                      "[@{http://www.w3.org/1999/xlink}to=\"%s\"]"
    href_attr_xpath = "{http://www.w3.org/1999/xlink}href"
    label_attr_xpath = "{http://www.w3.org/1999/xlink}label"
    locs = pre_elem.findall(loc_xpath)

    for loc in locs:
        concept = loc.get(href_attr_xpath)
        concept_label = loc.get(label_attr_xpath)
        if concept not in found_labels:
            found_labels[concept] = {}
        pre_arcs = pre_elem.findall(pre_arc_xpath % concept_label)
        for pre_arc in pre_arcs:
            element = pre_arc.get("preferredLabel")
            if element not in found_labels[concept]:
                found_labels[concept][element] = True

    return found_labels

def clean_labels(lab_elem, pre_elem):
    """Search through the provided label element's children for labels and
    delete any that are not being used by the presentation element.

    """
    #Label types which are never presented, and therefor shouldn't be deleted
    #unless their associated concept is not used.
    standard_labels = [
        "http://www.xbrl.org/2003/role/label",
        "http://www.xbrl.org/2003/role/documentation",
        "http://www.xbrl.org/2003/role/definitionGuidance",
        "http://www.xbrl.org/2003/role/disclosureGuidance",
        "http://www.xbrl.org/2003/role/presentationGuidance",
        "http://www.xbrl.org/2003/role/measurementGuidance",
        "http://www.xbrl.org/2003/role/commentaryGuidance",
        "http://www.xbrl.org/2003/role/exampleGuidance"
    ]
    #XPath for the containing label link element.
    label_link_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelLink"
    #Retrieve a dictionary of all labels in the label linkbase.
    labels = get_labels(lab_elem)
    #Retrieve a dictionary of all label types used in the presentation linkbase.
    used_labels = get_used_labels(pre_elem)
    #Get the parent element of all labels, so they can be accessed for removal.
    label_link = lab_elem.find(label_link_xpath)
    #Create an empty dictionary for logging removed labels.
    removed_labels = {}
    #For each concept that has a label.
    for concept, label_types in labels.items():
        #If the concept is not presented at all.
        if concept not in used_labels:
            #Log and delete every label that belongs to the concept.
            removed_labels, label_link = delete_label(
                removed_labels,
                concept,
                label_link
            )
        #If the concept is presented.
        else:
            #Create a store for the label types to delete.
            store = []
            #For each type of label.
            for label_type in label_types:
                #If the label type isn't used and it is a presentational type.
                if (label_type not in used_labels[concept] and
                    label_type not in standard_labels):
                    #Add it to the store of label types to delete.
                    store.append(label_type)
            #If there are label types to remove.
            if store:
                #Remove the labels and log them.
                removed_labels, label_link = delete_label(
                    removed_labels,
                    concept,
                    label_link,
                    store
                )
    #Return a dictionary of the labels which have been removed.
    return removed_labels

def delete_label(removed_labels, concept, label_link, label_types=False):
    """Accepts a dictionary of removed labels, a concept, a label_link element
    full of labels, and possibly a type of label to delete. If the label type
    isn't provided, all of the concepts labels are deleted, otherwise, only the
    label of the provided type is removed.

    """
    #XPath expressions which will be used later.
    label_xpath = ".//{http://www.xbrl.org/2003/linkbase}label" \
                  "[@{http://www.w3.org/1999/xlink}label=\"%s\"]"
    loc_href_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc" \
                     "[@{http://www.w3.org/1999/xlink}href=\"%s\"]"
    label_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelArc" \
                      "[@{http://www.w3.org/1999/xlink}from=\"%s\"]"
    role_attr_xpath = "{http://www.w3.org/1999/xlink}role"
    to_attr_xpath = "{http://www.w3.org/1999/xlink}to"
    label_attr_xpath = "{http://www.w3.org/1999/xlink}label"

    #If the concept has already been logged.
    if concept not in removed_labels:
        #Log it.
        removed_labels[concept] = {}
    #Our default stance is not to delete the labels related arc.
    delete_arc = False
    #Find all locators for the passed concept. There are usually only one.
    locs_to_delete = label_link.findall(loc_href_xpath % concept)
    #For each locator that is found.
    for loc_to_delete in locs_to_delete:
        #Store the element label reference.
        label_ref = loc_to_delete.get(label_attr_xpath)
        #Use the label reference to find all of the elements arcs.
        label_arcs_to_delete = label_link.findall(label_arc_xpath % label_ref)
        #For each arc.
        for label_arc_to_delete in label_arcs_to_delete:
            #Store the reference to the label.
            to_label = label_arc_to_delete.get(to_attr_xpath)
            #Use the reference to the label, to find every label.
            labels_to_delete = label_link.findall(label_xpath % to_label)
            #For each label.
            for label_to_delete in labels_to_delete:
                #Store the label type.
                label_role = label_to_delete.get(role_attr_xpath)
                #If the label type is in the passed types, or no types were
                #passed at all.
                if not label_types or label_role in label_types:
                    #Log the label we are about to delete.
                    removed_labels[concept][label_role] = label_to_delete.text
                    #Delete the label.
                    label_link.remove(label_to_delete)
                    #Delete the arc later.
                    delete_arc = True
            #If we said to delete the arc.
            if delete_arc:
                #Delete it.
                label_link.remove(label_arc_to_delete)
                #And reset for the next arc.
                delete_arc = False
        #Check if there are any arcs referencing the locater.
        label_arcs_to_delete = label_link.findall(label_arc_xpath % label_ref)
        #If there aren't.
        if not label_arcs_to_delete:
            #Delete the locater.
            label_link.remove(loc_to_delete)
    #Return the log of delete labels and the element they were deleted from.
    return (removed_labels, label_link)

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
    for context, identifier in contexts.items():
        fact_values_xpath = ".//*[@contextRef='%s']" % str(identifier)
        fact_value = elem.find(fact_values_xpath)
        if fact_value is None:
            contexts_removed.append(identifier)
            elem.remove(context)

    return contexts_removed

def get_linkbase(filename, linkbase):
    """Find the requested linkbase in the provided element's DTS."""
    #Store the path to filename.
    path = filename.rsplit("/", 1)[0] + "/"
    #Parse the instance document.
    tree = namespace.parse_xmlns(filename)
    #Grab the root element.
    root = tree.getroot()
    #Find the element containing the schema reference.
    schema_ref = root.find(".//{http://www.xbrl.org/2003/linkbase}schemaRef")
    #Grab the schema reference.
    schema = schema_ref.get("{http://www.w3.org/1999/xlink}href")
    #Overwrite the instance filename with the schema.
    filename = path + schema
    #If the schema was requested, return it.
    if linkbase == "xsd":
        return filename
    #Parse the schema.
    tree = namespace.parse_xmlns(filename)
    #Grab the root element.
    root = tree.getroot()
    #Store the xpath expression for retrieving linkbase references.
    linkbase_refs_xpath = ".//{http://www.xbrl.org/2003/linkbase}linkbaseRef"
    #Retrieve all linkbase references.
    linkbase_refs = root.findall(linkbase_refs_xpath)
    #Create a dictionary for retrieving each type of linkbase.
    linkbases = {
        "pre": "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
        "def": "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
        "cal": "http://www.xbrl.org/2003/role/calculationLinkbaseRef",
        "lab": "http://www.xbrl.org/2003/role/labelLinkbaseRef"
    }
    #Store the xpath expression for retrieving role attributes.
    role_xpath = "{http://www.w3.org/1999/xlink}role"
    #For each linkbase reference.
    for linkbase_ref in linkbase_refs:
        #If the linkbase reference matches the requested linkbase.
        if linkbase_ref.get(role_xpath) == linkbases[linkbase]:
            #Return the matching full linkbase filename.
            return path + linkbase_ref.get("{http://www.w3.org/1999/xlink}href")

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

            parent = parent.split("#")[-1]
            child = child.split("#")[-1]

            if parent not in store[link_role_href]:
                store[link_role_href][parent] = []
            store[link_role_href][parent].append(child)

    for linkrole, totals in store.items():
        for total, sum_elements in totals.items():
            sum_elements.sort()
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
