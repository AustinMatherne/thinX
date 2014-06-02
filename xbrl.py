#!/usr/bin/env python

import configparser
import collections
import re
from lxml import etree
from decimal import Decimal
from datetime import datetime


def get_file_namespace(filename):
    xsd = get_linkbase(filename, "xsd")
    tree = etree.parse(xsd)
    root = tree.getroot()
    name = root.get("targetNamespace")
    for key, value in root.nsmap.items():
        if value == name:
            prefix = key
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


def add_namespace(elem, registry):
    """Accepts an element, and a prefix, a namespace, and a list of measures.
    Declares the namespace and prefix in the provided element, searches through
    the element's children for declared units of measure. For each measure that
    is found, it executes a case insensitive search against the supplied list
    of measures for a match, if a match is found, the measure and its prefix
    are replaced with the provided prefix and clean measure.

    """
    log = {}
    measure_xpath = ".//{http://www.xbrl.org/2003/instance}measure"

    def add_prefix(elem, prefix, ns):
        if prefix not in elem.nsmap:
            nsmap = elem.nsmap
            nsmap[prefix] = ns
            new_elem = etree.Element(elem.tag, nsmap=nsmap)
            new_elem[:] = elem[:]
            for key, value in elem.attrib.items():
                    new_elem.set(key, value)
            return new_elem
        else:
            return elem

    for base in registry:
        clean_measures = registry[base]["Measures"]
        prefix = registry[base]["Prefix"]
        ns = registry[base]["Namespace"]
        low_clean = [x.lower() for x in clean_measures]
        low_clean = [
            key
            for key, value in collections.Counter(low_clean).items()
            if value > 1
        ]
        current_measures = elem.findall(measure_xpath)
        for element in current_measures:
            current = element.text.split(":")
            if len(current) > 1:
                noprefix = False
                current = current[1]
            else:
                noprefix = True
                current = current[0]
            for clean in clean_measures:
                clean_lower = clean.lower()
                if current.lower() == clean_lower:
                    old = element.text
                    if noprefix:
                        new = clean
                    else:
                        new = prefix + ":" + clean
                    if new != old:
                        if (current != clean and clean_lower in low_clean):
                            pass
                        else:
                            element.text = new
                            log[old] = new

        elem = add_prefix(elem, prefix, ns)

    return (elem, log)


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
        for unit_set in units:
            prefix = units[unit_set]["Prefix"]
            for measure in units[unit_set]["Measures"]:
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
    # Label types which are never presented, and therefor shouldn't be deleted
    # unless their associated concept is not used.
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
    label_link_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelLink"
    labels = get_labels(lab_elem)
    used_labels = get_used_labels(pre_elem)
    label_link = lab_elem.find(label_link_xpath)
    removed_labels = {}
    for concept, label_types in labels.items():
        if concept not in used_labels:
            removed_labels, label_link = delete_label(
                removed_labels,
                concept,
                label_link
            )
        else:
            store = []
            for label_type in label_types:
                if (label_type not in used_labels[concept] and
                        label_type not in standard_labels):
                    store.append(label_type)
            if store:
                removed_labels, label_link = delete_label(
                    removed_labels,
                    concept,
                    label_link,
                    store
                )
    return removed_labels


def redundant_labels(lab_elem, pre_elem):
    """Search through the provided label element's children for concepts with
    redundant labels and consolidate them. Also update the presentation element
    so that if the labels are identical, it doesn't point to more than one type
    of label for a concept.

    """
    label_link_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelLink"
    label_link = lab_elem.find(label_link_xpath)
    labels = get_labels(lab_elem)

    regular_label_types = {
        "http://www.xbrl.org/2003/role/terseLabel": 0,
        "http://www.xbrl.org/2003/role/verboseLabel": 1
    }
    positive_label_types = {
        "http://www.xbrl.org/2003/role/positiveLabel": 2,
        "http://www.xbrl.org/2003/role/positiveTerseLabel": 3,
        "http://www.xbrl.org/2003/role/positiveVerboseLabel": 4
    }
    negative_label_types = {
        "http://www.xbrl.org/2003/role/negativeLabel": 2,
        "http://www.xbrl.org/2003/role/negativeTerseLabel": 3,
        "http://www.xbrl.org/2003/role/negativeVerboseLabel": 4
    }
    zero_label_types = {
        "http://www.xbrl.org/2003/role/zeroLabel": 2,
        "http://www.xbrl.org/2003/role/zeroTerseLabel": 3,
        "http://www.xbrl.org/2003/role/zeroVerboseLabel": 4
    }
    pos_label_types = dict(
        list(regular_label_types.items())
        + list(positive_label_types.items())
        + list(negative_label_types.items())
        + list(zero_label_types.items())
    )
    neg_label_types = {
        "http://www.xbrl.org/2009/role/negatedLabel": 0,
        "http://www.xbrl.org/2009/role/negatedTerseLabel": 1
    }

    result = {}

    def add_to_result(concept, base_label_types, label_type, store_label_type):
        if concept not in result:
            result[concept] = {}
        if base_label_types[label_type] > base_label_types[store_label_type]:
            result[concept][label_type] = store_label_type
        else:
            result[concept][store_label_type] = label_type

    removed_labels = {}
    for concept, label_types in labels.items():
        store = {}
        for label_type, label in label_types.items():
            for store_label_type, store_label in store.items():
                if label == store_label:
                    if (label_type in pos_label_types and
                            store_label_type in pos_label_types):
                        if (label_type in regular_label_types or
                                store_label_type in regular_label_types):
                            add_to_result(
                                concept,
                                pos_label_types,
                                label_type,
                                store_label_type
                            )
                        elif (label_type in positive_label_types and
                              store_label_type in positive_label_types):
                            add_to_result(
                                concept,
                                positive_label_types,
                                label_type,
                                store_label_type
                            )
                        elif (label_type in negative_label_types and
                              store_label_type in negative_label_types):
                            add_to_result(
                                concept,
                                negative_label_types,
                                label_type,
                                store_label_type
                            )
                        elif (label_type in zero_label_types and
                              store_label_type in zero_label_types):
                            add_to_result(
                                concept,
                                zero_label_types,
                                label_type,
                                store_label_type
                            )
                    elif (label_type in neg_label_types and
                          store_label_type in neg_label_types):
                        add_to_result(
                            concept,
                            neg_label_types,
                            label_type,
                            store_label_type
                        )
            store[label_type] = label

    unclean = True
    while unclean:
        unclean = False
        for concept in result:
            store = result[concept].keys()
            for key, value in result[concept].items():
                if value in store:
                    result[concept][key] = result[concept][value]
                    unclean = True

    for concept, label_types in result.items():
        removed_labels, label_link = delete_label(
            removed_labels,
            concept,
            label_link,
            label_types
        )
        for label_type, label in label_types.items():
            pre_elem = change_preferred_label(
                concept,
                pre_elem,
                label_type,
                label
            )
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
    label_xpath = ".//{http://www.xbrl.org/2003/linkbase}label" \
                  "[@{http://www.w3.org/1999/xlink}label='%s']"
    loc_href_xpath = ".//{http://www.xbrl.org/2003/linkbase}loc" \
                     "[@{http://www.w3.org/1999/xlink}href='%s']"
    label_arc_xpath = ".//{http://www.xbrl.org/2003/linkbase}labelArc" \
                      "[@{http://www.w3.org/1999/xlink}from='%s']"
    role_attr_xpath = "{http://www.w3.org/1999/xlink}role"
    to_attr_xpath = "{http://www.w3.org/1999/xlink}to"
    label_attr_xpath = "{http://www.w3.org/1999/xlink}label"

    if concept not in removed_labels:
        removed_labels[concept] = {}
    delete_arc = False
    locs_to_delete = label_link.findall(loc_href_xpath % concept)
    for loc_to_delete in locs_to_delete:
        label_ref = loc_to_delete.get(label_attr_xpath)
        label_arcs_to_delete = label_link.findall(label_arc_xpath % label_ref)
        for label_arc_to_delete in label_arcs_to_delete:
            to_label = label_arc_to_delete.get(to_attr_xpath)
            labels_to_delete = label_link.findall(label_xpath % to_label)
            for label_to_delete in labels_to_delete:
                label_role = label_to_delete.get(role_attr_xpath)
                if not label_types or label_role in label_types:
                    removed_labels[concept][label_role] = label_to_delete.text
                    label_link.remove(label_to_delete)
                    delete_arc = True
            if delete_arc:
                label_link.remove(label_arc_to_delete)
                delete_arc = False
        label_arcs_to_delete = label_link.findall(label_arc_xpath % label_ref)
        if not label_arcs_to_delete:
            label_link.remove(loc_to_delete)
    return (removed_labels, label_link)


def two_day_contexts(elem):
    """Return durational two day contexts defined in the provided element."""

    def days_between(d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    contexts = []
    context_xpath = ".//{http://www.xbrl.org/2003/instance}context"
    start_xpath = ".//{http://www.xbrl.org/2003/instance}startDate"
    end_xpath = ".//{http://www.xbrl.org/2003/instance}endDate"
    current_contexts = elem.findall(context_xpath)

    for context in current_contexts:
        start = context.find(start_xpath)
        if start is not None:
            end = context.find(end_xpath)
            if days_between(start.text, end.text) == 1:
                contexts.append(context.get("id"))

    return contexts


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
    xlink = "{http://www.w3.org/1999/xlink}href"
    path = filename.rsplit("/", 1)[0] + "/"
    tree = etree.parse(filename)
    root = tree.getroot()
    schema_ref = root.find(".//{http://www.xbrl.org/2003/linkbase}schemaRef")
    schema = schema_ref.get(xlink)
    filename = path + schema
    if linkbase == "xsd":
        return filename
    tree = etree.parse(filename)
    root = tree.getroot()
    linkbase_refs_xpath = ".//{http://www.xbrl.org/2003/linkbase}linkbaseRef"
    linkbase_refs = root.findall(linkbase_refs_xpath)
    linkbases = {
        "pre": "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
        "def": "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
        "cal": "http://www.xbrl.org/2003/role/calculationLinkbaseRef",
        "lab": "http://www.xbrl.org/2003/role/labelLinkbaseRef"
    }
    role_xpath = "{http://www.w3.org/1999/xlink}role"
    for linkbase_ref in linkbase_refs:
        if linkbase_ref.get(role_xpath) == linkbases[linkbase]:
            return path + linkbase_ref.get(xlink)


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
            weight = arc.get("weight")
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
            store[link_role_href][parent].append((child, weight))

    for linkrole, totals in store.items():
        for total, sum_elements in totals.items():
            sum_elements.sort(key=lambda tup: tup[0])
    return store


def dup_calcs(elem):
    """Return all duplicate calculation relationships in the given element."""
    store = get_calcs(elem)
    warnings = {}

    def add_warning(total):
        if total in warnings:
            warnings[total] += 1
        else:
            warnings[total] = 0

    base_calcs = {}
    for linkrole in store:
        for total in store[linkrole]:
            if total in base_calcs:
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
            else:
                base_calcs[total] = [store[linkrole][total]]

    return warnings


def calc_values(elem, calcs):
    """Return all calculation inconsistencies for the given concepts in the
    provided element.

    """
    nsmap = elem.nsmap
    warnings = []
    for link_role, total_elems in calcs.items():
        for total_elem, line_items in total_elems.items():
            total_split = total_elem.split("_", 1)
            namespace = nsmap[total_split[0]]
            totals = elem.findall(".//{%s}%s" % (namespace, total_split[-1]))
            for total in totals:
                value = Decimal(total.text)
                cont = total.get("contextRef")
                calculated_total = 0
                changed = False
                for line_item in line_items:
                    weight = line_item[1]
                    line_item_split = line_item[0].split("_", 1)
                    ns = (nsmap[line_item_split[0]], line_item_split[-1], cont)
                    new = elem.find(".//{%s}%s[@contextRef='%s']" % ns)
                    if new is not None and new.text is not None:
                        changed = True
                        if float(weight) == 1:
                            calculated_total += Decimal(new.text)
                        else:
                            calculated_total -= Decimal(new.text)
                if calculated_total != value and changed:
                    warnings.append([link_role,
                                    total_elem.split("}")[-1],
                                    cont,
                                    value,
                                    calculated_total])

    return warnings


def link_role_def(elem, link_role):
    """Take a link role URI and return the definition."""
    xpath = ".//*[@roleURI='%s']/{http://www.xbrl.org/2003/linkbase}definition"
    definition = elem.find(xpath % link_role).text

    return definition


def insert_labels(elem, calcs):
    """Take a list of calcs and insert standard labels before each concept."""
    role_label = "http://www.xbrl.org/2003/role/label"
    xlink = "{http://www.w3.org/1999/xlink}%s"
    loc_xpath = ".//*[@{http://www.w3.org/1999/xlink}href='%s']"
    arc_xpath = ".//*[@{http://www.w3.org/1999/xlink}from='%s']"
    lab_xpath = ".//*[@{http://www.w3.org/1999/xlink}label='%s']"
    locs = elem.findall(".//{http://www.xbrl.org/2003/linkbase}loc")
    concepts = {}
    for loc in locs:
        href = loc.get(xlink % "href")
        concepts[href.split("#")[-1]] = href
    for calc in calcs:
        stn_lab = ""
        if calc[1] in concepts:
            href = concepts[calc[1]]
            label = elem.find(loc_xpath % href).get(xlink % "label")
            arcs = elem.findall(arc_xpath % label)
            for arc in arcs:
                lab = elem.find(lab_xpath % arc.get(xlink % "to"))
                if lab.get(xlink % "role") == role_label:
                    stn_lab = lab.text
                    break

        calc.insert(1, stn_lab)

    return calcs


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

    def change_ns(elem, old_namespace, new_namespace):
        for prefix, namespace in elem.nsmap.items():
            if namespace == old_namespace:
                nsmap = elem.nsmap
                nsmap[prefix] = new_namespace
                new_elem = etree.Element(elem.tag, nsmap=nsmap)
                new_elem[:] = elem[:]
                for key, value in elem.attrib.items():
                    new_elem.set(key, value)
                return new_elem

    old_namespace = elem.get("targetNamespace")
    new_namespace = re.search("(^.*)/\d{8}$", old_namespace).group(1)
    elem.set("targetNamespace", new_namespace)

    elem = change_ns(elem, old_namespace, new_namespace)

    return (elem, (old_namespace, new_namespace))


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


def retrieve_base(elem):
    """Return the base taxonomy from the provided schema element."""
    version = ""
    ugt = re.compile("(us-gaap-\d{4}-\d{2}-\d{2})\.xsd$")
    imports = elem.findall("{http://www.w3.org/2001/XMLSchema}import")

    for schema in imports:
        location = ugt.search(schema.get("schemaLocation"))
        if location:
            version = location.group(1)
            break

    return version


def get_link_roles(elem):
    """Return all extension link role URIs found in the given element."""
    log = []
    role_type_xpath = ".//{http://www.xbrl.org/2003/linkbase}roleType"
    link_roles = elem.findall(role_type_xpath)

    for link_role in link_roles:
        log.append(link_role.get("roleURI"))

    return log


def get_active_link_roles(linkbases):
    """Return a set of all extension link roles in use by the given linkbases.

    """
    log = []
    xpaths = {"pre": ".//{http://www.xbrl.org/2003/linkbase}presentationLink",
              "def": ".//{http://www.xbrl.org/2003/linkbase}definitionLink",
              "cal": ".//{http://www.xbrl.org/2003/linkbase}calculationLink"}
    role_attr_xpath = "{http://www.w3.org/1999/xlink}role"

    for key, value in linkbases.items():
        if key in xpaths:
            link_roles = value["root"].findall(xpaths[key])
            for link_role in link_roles:
                log.append(link_role.get(role_attr_xpath))

    return set(log)


def compare_link_roles(roles, active_roles):
    """Return any extension link roles which are not active."""
    log = []
    for role in roles:
        if role not in active_roles:
            log.append(role)

    return log


def delete_link_roles(elem, link_roles):
    """Delete the provided link roles from the given element."""
    role_type_attr_xpath = ".//*[@roleURI='%s']"
    app_info = elem.find(".//{http://www.w3.org/2001/XMLSchema}appinfo")
    log = []

    for link_role in link_roles:
        role = elem.find(role_type_attr_xpath % link_role)
        app_info.remove(role)
        log.append(link_role)

    return log
