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
                    if (current_measure != clean_measure and
                        clean_measure_lower in low_clean_measures):
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
                  "[@{http://www.w3.org/1999/xlink}label='%s']"
    label_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelArc" \
                      "[@{http://www.w3.org/1999/xlink}from='%s']"
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
                      "[@{http://www.w3.org/1999/xlink}to='%s']"
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

def redundant_labels(lab_elem, pre_elem):
    """Search through the provided label element's children for concepts with
    redundant labels and consolidate them. Also update the presentation element
    so that if the labels are identical, it doesn't point to more than one type
    of label for a concept.

    """
    #XPath for the label link.
    label_link_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelLink"
    #Get the label link.
    label_link = lab_elem.find(label_link_xpath)
    #Get a dictionary containing every concept with all of it's labels.
    labels = get_labels(lab_elem)

    #Presentational label types which all non negated labels can be reduced to.
    regular_label_types = {
        "http://www.xbrl.org/2003/role/terseLabel": 0,
        "http://www.xbrl.org/2003/role/verboseLabel": 1
    }
    #Positive label types.
    positive_label_types = {
        "http://www.xbrl.org/2003/role/positiveLabel": 2,
        "http://www.xbrl.org/2003/role/positiveTerseLabel": 3,
        "http://www.xbrl.org/2003/role/positiveVerboseLabel": 4
    }
    #Negative label types.
    negative_label_types = {
        "http://www.xbrl.org/2003/role/negativeLabel": 2,
        "http://www.xbrl.org/2003/role/negativeTerseLabel": 3,
        "http://www.xbrl.org/2003/role/negativeVerboseLabel": 4
    }
    #Zero label types.
    zero_label_types = {
        "http://www.xbrl.org/2003/role/zeroLabel": 2,
        "http://www.xbrl.org/2003/role/zeroTerseLabel": 3,
        "http://www.xbrl.org/2003/role/zeroVerboseLabel": 4
    }
    #Combine all none negated label types that can be reduced.
    pos_label_types = dict(
        list(regular_label_types.items())
        + list(positive_label_types.items())
        + list(negative_label_types.items())
        + list(zero_label_types.items())
    )
    #Negated label types.
    neg_label_types = {
        "http://www.xbrl.org/2009/role/negatedLabel": 0,
        "http://www.xbrl.org/2009/role/negatedTerseLabel": 1
    }

    #The object to return.
    result = {}

    def add_to_result(concept, base_label_types, label_type, store_label_type):
        #If concept isn't already in the results dictionary.
        if concept not in result:
            #Create an empty dictionary in it's place.
            result[concept] = {}
        #If the label type has a lower precedence than the store label type.
        if base_label_types[label_type] > base_label_types[store_label_type]:
            #Record the label type to be overridden by the store label type.
            result[concept][label_type] = store_label_type
        #If the label type has a higher precedence than the store label type.
        else:
            #Record the store label type to be overridden by the label type.
            result[concept][store_label_type] = label_type

    #Only needed to pass to the delete label function.
    removed_labels = {}
    #For each concept with a label.
    for concept, label_types in labels.items():
        #Base store to compare against.
        store = {}
        #For each label type of concept.
        for label_type, label in label_types.items():
            #For each label in store.
            for store_label_type, store_label in store.items():
                #If label matches another label in store.
                if label == store_label:
                    #If both the label and store label are presentable, and
                    #aren't negated, total, net, period start, or end types.
                    if (label_type in pos_label_types and
                        store_label_type in pos_label_types):
                        #If either the label or store label are regular types.
                        if (label_type in regular_label_types or
                            store_label_type in regular_label_types):
                            add_to_result(
                                concept,
                                pos_label_types,
                                label_type,
                                store_label_type
                            )
                        #If both the label and store label are positive types.
                        elif (label_type in positive_label_types and
                              store_label_type in positive_label_types):
                            add_to_result(
                                concept,
                                positive_label_types,
                                label_type,
                                store_label_type
                            )
                        #If both the label and store label are negative types.
                        elif (label_type in negative_label_types and
                              store_label_type in negative_label_types):
                            add_to_result(
                                concept,
                                negative_label_types,
                                label_type,
                                store_label_type
                            )
                        #If both the label and store label are zero types.
                        elif (label_type in zero_label_types and
                              store_label_type in zero_label_types):
                            add_to_result(
                                concept,
                                zero_label_types,
                                label_type,
                                store_label_type
                            )
                    #If both the label and store label are negated types.
                    elif (label_type in neg_label_types and
                          store_label_type in neg_label_types):
                        add_to_result(
                            concept,
                            neg_label_types,
                            label_type,
                            store_label_type
                        )
            #Add the label to the store.
            store[label_type] = label

    #Make sure the while loop runs at least once.
    unclean = True
    #Start the loop.
    while unclean:
        #Unless we change something, the loop should only run once.
        unclean = False
        #For concept in the result dictionary.
        for concept in result:
            #Save a reference to all of the label types that need to change.
            store = result[concept].keys()
            #For each label type of the concept that has so far been set to be
            #overridden.
            for key, value in result[concept].items():
                #If the label type we are changing to is being replacing itself.
                if value in store:
                    #Change it to that new label type, as well.
                    result[concept][key] = result[concept][value]
                    #And make sure we loop again.
                    unclean = True

    #For each concept in results.
    for concept, label_types in result.items():
        #Delete all labels which have been reported for deletion.
        removed_labels, label_link = delete_label(
            removed_labels,
            concept,
            label_link,
            label_types
        )
        #For label type of concept.
        for label_type, label in label_types.items():
            #Swap out the deleted label with the identical still existing label.
            pre_elem = change_preferred_label(
                concept,
                pre_elem,
                label_type,
                label
            )
    #Return the concepts along with their labels which were removed.
    return result

def change_preferred_label(concept, pre_elem, old_label_type, new_label_type):
    """Accepts a concept, a presentation link element, a label type to remove
    and the label type to use in it's place.

    """
    loc_href_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc" \
                     "[@{http://www.w3.org/1999/xlink}href='%s']"
    label_attr_xpath = "{http://www.w3.org/1999/xlink}label"
    to_attr_xpath = ".//{http://www.xbrl.org/2003/linkbase}presentationArc" \
                    "[@{http://www.w3.org/1999/xlink}to='%s']"
    keep = pre_elem.findall(loc_href_xpath % concept)

    for thing in keep:
        label = thing.get(label_attr_xpath)
        arcs = pre_elem.findall(to_attr_xpath % label)
        for arc in arcs:
            if arc.get("preferredLabel") == old_label_type:
                arc.set("preferredLabel", new_label_type)

    return pre_elem

def delete_label(removed_labels, concept, label_link, label_types=False):
    """Accepts a dictionary of removed labels, a concept, a label_link element
    full of labels, and possibly a type of label to delete. If the label type
    isn't provided, all of the concepts labels are deleted, otherwise, only the
    label of the provided type is removed.

    """
    #XPath expressions which will be used later.
    label_xpath = ".//{http://www.xbrl.org/2003/linkbase}label" \
                  "[@{http://www.w3.org/1999/xlink}label='%s']"
    loc_href_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc" \
                     "[@{http://www.w3.org/1999/xlink}href='%s']"
    label_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelArc" \
                      "[@{http://www.w3.org/1999/xlink}from='%s']"
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

def clean_concepts(xsd_elem, pre_elem, def_elem, cal_elem, lab_elem, schema):
    """Search through the provided xsd element's children for concepts. Find any
    that aren't referenced by the presentation, definition, calculation, or
    label linkbases and remove them.

    """
    concepts_removed = []
    concepts_xpath = ".//{http://www.w3.org/2001/XMLSchema}element"
    href_xpath = ".//*[@{http://www.w3.org/1999/xlink}href='%s#%s']"
    current_concepts = xsd_elem.findall(concepts_xpath)
    for element in current_concepts:
        identifier = element.get("id")
        in_pre = pre_elem.findall(href_xpath % (schema, identifier))
        in_def = def_elem.findall(href_xpath % (schema, identifier))
        in_cal = cal_elem.findall(href_xpath % (schema, identifier))
        in_lab = lab_elem.findall(href_xpath % (schema, identifier))
        if not in_pre and not in_def and not in_cal and not in_lab:
            xsd_elem.remove(element)
            concepts_removed.append(identifier)

    return concepts_removed

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
    label_attr_xpath = "[@{http://www.w3.org/1999/xlink}label='%s']"
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

def link_role_sort(elem):
    """Update link role sort codes to improve compatibility with Crossfire."""
    log = []

    dei = "0000"
    face_fin = re.compile("^00[1-9]0$")
    face_par = re.compile("^00[1-9]{2}$")
    text_block = re.compile("^[1-3]\d{3}$")
    level_four = re.compile("^4\d{3}$")
    eights = re.compile("^8\d{3}$")
    sort_reg = re.compile("^(\d+)(.+)$")

    linkbase_refs_xpath = ".//{http://www.xbrl.org/2003/linkbase}definition"
    linkbase_refs = elem.findall(linkbase_refs_xpath)

    for linkbase_ref in linkbase_refs:
        match = sort_reg.search(linkbase_ref.text)
        sort = match.group(1)
        link_def = match.group(2)
        new_sort = sort
        if sort == dei:
            new_sort = "00090"
        elif face_par.search(sort):
            new_sort = sort[:3] + "0" + sort[-1:]
        elif text_block.search(sort):
            new_sort = sort[:3] + "0" + sort[:1]
        elif face_fin.search(sort) or eights.search(sort):
            new_sort = sort + "0"
        elif level_four.search(sort):
            code = int(sort[-1:]) + 1
            if code < 10:
                new_sort = sort[:-1] + "0" + str(code)
            else:
                new_sort = sort[:-1] + str(code)

        if sort != new_sort:
            log.append((sort, new_sort))
            linkbase_ref.text = new_sort + link_def
    log.sort(key=lambda tup: tup[0])

    return log

def remove_namespace_date(elem):
    """Remove the date from the targetNamespcae."""
    old_namespace = elem.get("targetNamespace")
    new_namespace = re.search("(^.*)/\d{8}$", old_namespace).group(1)
    elem.set("targetNamespace", new_namespace)
    attrs = elem.items()
    for attr in attrs:
        if attr[-1] == old_namespace:
            elem.set(attr[0], new_namespace)
            break

    return (old_namespace, new_namespace)

def rename_refs(elem, linkbase):
    """Rename linkbase references in element to tic-current_taxonomy."""
    log = []
    filename = re.compile("^(.*)(\d{8})(.*)$")
    href_attr_xpath = "{http://www.w3.org/1999/xlink}href"
    path = re.compile("^(?!http://)(.+-)(\d{8})(\.xsd)(#.+)$")
    if linkbase == "xsd":
        link_refs_xpath = ".//{http://www.xbrl.org/2003/linkbase}linkbaseRef"
        link_refs = elem.findall(link_refs_xpath)
        for link_ref in link_refs:
            old_path = link_ref.get(href_attr_xpath)
            match = filename.search(old_path)
            new_path = match.group(1) + "current_taxonomy" + match.group(3)
            link_ref.set(href_attr_xpath, new_path)
            log.append((old_path, new_path))
        base = match.group(1) + match.group(2)
        log.append((base + ".xsd", match.group(1) + "current_taxonomy.xsd"))
        log.append((base + ".xml", "*Deleted*"))
    else:
        links = ["loc"]
        if linkbase == "linkbase":
            links.append("roleRef")
        for link in links:
            xpath = ".//{http://www.xbrl.org/2003/linkbase}%s" % link
            link_refs = elem.findall(xpath)
            for link_ref in link_refs:
                match = path.search(link_ref.get(href_attr_xpath))
                if match:
                    xsd = match.group(1) + "current_taxonomy" + match.group(3)
                    link_ref.set(href_attr_xpath, xsd + match.group(4))

    return log
