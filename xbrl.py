#!/usr/bin/env python

import configparser
import collections
import re
from lxml import etree
from decimal import Decimal
from datetime import datetime


def open_linkbases(entry, files):
    """Opens the list of files using the provided taxonomy entry point."""
    linkbases = {}
    for key in files:
        linkbases[key] = {}
        try:
            linkbases[key]["filename"] = get_linkbase(entry, key)
            linkbases[key]["tree"] = etree.parse(linkbases[key]["filename"])
            linkbases[key]["root"] = linkbases[key]["tree"].getroot()
        except Exception as e:
            e.value = key
            raise e

    return linkbases


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
    registries = {}
    for section in config.sections():
        registries[section] = {}
        registries[section]["Prefix"] = config[section]["Prefix"]
        registries[section]["Namespace"] = config[section]["Namespace"]
        clean_measures = []
        for measure in config[section]["Measures"].split(","):
            clean_measures.append(measure.lstrip('\n'))
        registries[section]["Measures"] = clean_measures

    if filename:
        file_namespace = get_file_namespace(filename)
        registries["BASE"]["Namespace"] = file_namespace["namespace"]
        registries["BASE"]["Prefix"] = file_namespace["prefix"]

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
        for element in elem.iterfind(measure_xpath):
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
                        new = "{0}:{1}".format(prefix, clean)
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
    for element in elem.iterfind(measure_xpath):
        logit = True
        for unit_set in units:
            prefix = units[unit_set]["Prefix"]
            for measure in units[unit_set]["Measures"]:
                if len(element.text.split(":")) > 1:
                    if "{0}:{1}".format(prefix, measure) == element.text:
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
    xlink = "{http://www.w3.org/1999/xlink}"
    linkbase = "{http://www.xbrl.org/2003/linkbase}"
    role_attr_xpath = "{0}role".format(xlink)
    to_attr_xpath = "{0}to".format(xlink)
    from_attr_xpath = "{0}from".format(xlink)
    href_attr_xpath = "{0}href".format(xlink)
    label_attr_xpath = "{0}label".format(xlink)
    lab_link = lab_elem.find(".//{0}labelLink".format(linkbase))

    loc = "{0}loc".format(linkbase)
    label_arc = "{0}labelArc".format(linkbase)
    label = "{0}label".format(linkbase)
    locs = {}
    label_arcs = {}
    labels = {}

    for elem in lab_link.iter():
        if elem.tag == loc:
            locs[elem.get(label_attr_xpath)] = elem.get(href_attr_xpath)
        elif elem.tag == label_arc:
            label_arcs[elem.get(to_attr_xpath)] = elem.get(from_attr_xpath)
        elif elem.tag == label:
            labels[(elem.get(label_attr_xpath), elem.get(role_attr_xpath))] = {
                "type": elem.get(role_attr_xpath),
                "label": elem.text
            }

    for lab, label_type in labels.items():
        href = locs[label_arcs[lab[0]]]
        found_labels.setdefault(
            href,
            dict()
        )[label_type["type"]] = label_type["label"]
    return found_labels


def get_used_labels(pre_elem):
    """Return a dictionary listing all active labels in the element."""
    found_labels = {}
    xlink = "{http://www.w3.org/1999/xlink}"
    linkbase = ".//{http://www.xbrl.org/2003/linkbase}"
    arc_xpath = "{0}presentationArc[@{1}to='%s']".format(linkbase, xlink)
    href_attr_xpath = "{0}href".format(xlink)
    lab_attr_xpath = "{0}label".format(xlink)
    loc_xpath = "{0}loc".format(linkbase)

    for link in pre_elem.iterfind("{0}presentationLink".format(linkbase)):
        for loc in link.iterfind(loc_xpath):
            concept = loc.get(href_attr_xpath)
            if concept not in found_labels:
                found_labels[concept] = {}
            for pre_arc in link.iterfind(arc_xpath % loc.get(lab_attr_xpath)):
                element = pre_arc.get("preferredLabel")
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
    used_labels = get_used_labels(pre_elem)
    labels = get_labels(lab_elem)
    to_delete = {}
    for concept, lab_types in labels.items():
        if concept not in used_labels:
            to_delete[concept] = "All"
        else:
            for lab_type in lab_types:
                not_used = lab_type not in used_labels[concept]
                not_standard = lab_type not in standard_labels
                if (not_used and not_standard):
                    to_delete.setdefault(concept, list()).append(lab_type)
    removed_labels, lab_elem = delete_labels(to_delete, lab_elem)

    return removed_labels


def redundant_labels(lab_elem, pre_elem):
    """Search through the provided label element's children for concepts with
    redundant labels and consolidate them. Also update the presentation element
    so that if the labels are identical, it doesn't point to more than one type
    of label for a concept.

    """

    def add_to_result(concept, base_label_types, label_type, store_label_type):
        if concept not in result:
            result[concept] = {}
        if base_label_types[label_type] > base_label_types[store_label_type]:
            result[concept][label_type] = store_label_type
        else:
            result[concept][store_label_type] = label_type

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

    for concept, label_types in get_labels(lab_elem).items():
        store = {}
        for label_type, label in label_types.items():
            for store_label_type, store_label in store.items():
                if label == store_label:
                    is_pos = label_type in pos_label_types
                    store_is_pos = store_label_type in pos_label_types
                    is_neg = label_type in neg_label_types
                    store_is_neg = store_label_type in neg_label_types
                    if (is_pos and store_is_pos):
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
                    elif (is_neg and store_is_neg):
                        add_to_result(
                            concept,
                            neg_label_types,
                            label_type,
                            store_label_type
                        )
            store[label_type] = label

    clean = False
    while not clean:
        clean = True
        for concept in result:
            keys = result[concept].keys()
            for key, value in result[concept].items():
                if value in keys:
                    result[concept][key] = result[concept][value]
                    clean = False

    removed_labels, lab_elem = delete_labels(result, lab_elem)
    pre_elem = change_preferred_labels(result, pre_elem)

    return result


def change_preferred_labels(concepts, pre_elem):
    """Accepts a dictionary of concepts, and a presentation link element. The
    dictionary container  a label type to remove
    and the label type to use in it's place.

    """
    linkbase = ".//{http://www.xbrl.org/2003/linkbase}"
    xlink = "{http://www.w3.org/1999/xlink}"
    loc_href_xpath = "{0}loc[@{1}href='%s']".format(linkbase, xlink)
    lab_attr_xpath = "{0}label".format(xlink)
    to_attr_xpath = "{0}presentationArc[@{1}to='%s']".format(linkbase, xlink)

    for concept, label_types in concepts.items():
        for loc in pre_elem.iterfind(loc_href_xpath % concept):
            for old_label_type, new_label_type in label_types.items():
                for arc in pre_elem.iterfind(
                    to_attr_xpath % loc.get(lab_attr_xpath)
                ):
                    if arc.get("preferredLabel") == old_label_type:
                        arc.set("preferredLabel", new_label_type)

    return pre_elem


def delete_labels(concepts, lab_elem):
    """Accepts a dictionary of concepts, and a label linkbase element. The
    dictionary of concepts contains concepts as keys, and a list of label types
    to remove as their values. The label types of the concepts are removed from
    the label linkbase element.

    """
    xlink = "{http://www.w3.org/1999/xlink}"
    linkbase = "{http://www.xbrl.org/2003/linkbase}"
    role_attr_xpath = "{0}role".format(xlink)
    to_attr_xpath = "{0}to".format(xlink)
    label_attr_xpath = "{0}label".format(xlink)
    lab_link = lab_elem.find(".//{0}labelLink".format(linkbase))
    label_xpath = ".//{0}label[@{1}label='%s']".format(linkbase, xlink)
    loc_href_xpath = ".//{0}loc[@{1}href='%s']".format(linkbase, xlink)
    label_arc_xpath = ".//{0}labelArc[@{1}from='%s']".format(linkbase, xlink)
    removed_labels = {}
    for concept, label_types in concepts.items():
        for loc_to_delete in lab_link.iterfind(loc_href_xpath % concept):
            label_ref = label_arc_xpath % loc_to_delete.get(label_attr_xpath)
            for label_arc_to_delete in lab_link.iterfind(label_ref):
                to_label = label_arc_to_delete.get(to_attr_xpath)
                for lab_to_delete in lab_link.iterfind(label_xpath % to_label):
                    lab_role = lab_to_delete.get(role_attr_xpath)
                    if label_types == "All" or lab_role in label_types:
                        removed_labels.setdefault(
                            concept, dict()
                        )[lab_role] = lab_to_delete.text
                        lab_link.remove(lab_to_delete)
                if not etree.iselement(lab_link.find(label_xpath % to_label)):
                    lab_link.remove(label_arc_to_delete)
            if not etree.iselement(lab_link.find(label_ref)):
                lab_link.remove(loc_to_delete)

    return (removed_labels, lab_elem)


def two_day_contexts(elem):
    """Return durational two day contexts defined in the provided element."""

    def days_between(d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    contexts = []
    instance_xpath = ".//{http://www.xbrl.org/2003/instance}"
    start_xpath = "{0}startDate".format(instance_xpath)
    end_xpath = "{0}endDate".format(instance_xpath)

    for context in elem.iterfind("{0}context".format(instance_xpath)):
        start = context.find(start_xpath)
        if start is not None:
            if days_between(start.text, context.find(end_xpath).text) == 1:
                contexts.append(context.get("id"))

    return contexts


def clean_contexts(elem):
    """Search through the provided element's children for contexts. Find the
    ones which are not in use and remove them.

    """
    contexts = {}
    contexts_removed = []
    context_ref_xpath = ".//*[@contextRef='{0}']"
    context_xpath = ".//{http://www.xbrl.org/2003/instance}context"
    for element in elem.iterfind(context_xpath):
        contexts[element] = element.get("id")
    for context, identifier in contexts.items():
        fact_value = elem.find(context_ref_xpath.format(str(identifier)))
        if fact_value is None:
            contexts_removed.append(identifier)
            elem.remove(context)

    return contexts_removed


def clean_concepts(linkbases):
    """Searches through the provided dictionary of linkbases using the xsd to
    build a list of extension concepts. Then finds any that aren't referenced
    by the presentation, definition, calculation, or label linkbases and
    removes them.

    """
    concepts_removed = []
    xlink = "{http://www.w3.org/1999/xlink}"
    schema = linkbases["xsd"]["filename"].split("/")[-1]
    href_xpath = ".//*[@{0}href='{1}#%s']".format(xlink, schema)
    concepts_xpath = ".//{http://www.w3.org/2001/XMLSchema}element"
    for concept in linkbases["xsd"]["root"].iterfind(concepts_xpath):
        identifier = concept.get("id")
        used = False
        for key, val in linkbases.items():
            exists = val["root"].find(href_xpath % identifier)
            if key != "xsd" and etree.iselement(exists):
                used = True
                break
        if not used:
            linkbases["xsd"]["root"].remove(concept)
            concepts_removed.append(identifier)

    return concepts_removed


def get_linkbase(filename, linkbase):
    """Find the requested linkbase in the provided element's DTS."""
    href_xpath = "{http://www.w3.org/1999/xlink}href"
    link_xpath = ".//{http://www.xbrl.org/2003/linkbase}"
    schema_xpath = "{0}schemaRef".format(link_xpath)
    path = "{0}/".format(filename.rsplit("/", 1)[0])
    tree = etree.parse(filename)
    root = tree.getroot()
    filename = path + root.find(schema_xpath).get(href_xpath)
    if linkbase == "xsd":
        return filename
    tree = etree.parse(filename)
    root = tree.getroot()
    linkbases = {
        "pre": "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
        "def": "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
        "cal": "http://www.xbrl.org/2003/role/calculationLinkbaseRef",
        "lab": "http://www.xbrl.org/2003/role/labelLinkbaseRef"
    }
    role_xpath = "{http://www.w3.org/1999/xlink}role"
    for linkbase_ref in root.iterfind("{0}linkbaseRef".format(link_xpath)):
        if linkbase_ref.get(role_xpath) == linkbases[linkbase]:
            return path + linkbase_ref.get(href_xpath)


def get_calcs(elem):
    """Return all calculation relationships discovered in the given element."""
    store = {}
    linkbase_xpath = ".//{http://www.xbrl.org/2003/linkbase}"
    xlink = "{http://www.w3.org/1999/xlink}"
    calc_link_xpath = "{0}calculationLink".format(linkbase_xpath)
    calc_arc_xpath = "{0}calculationArc".format(linkbase_xpath)
    calc_loc_xpath = "{0}loc".format(linkbase_xpath)
    from_xpath = "{0}from".format(xlink)
    to_xpath = "{0}to".format(xlink)
    role_xpath = "{0}role".format(xlink)
    href_xpath = "{0}href".format(xlink)
    lab_attr_xpath = "[@{0}label='%s']".format(xlink)
    for linkrole in elem.iterfind(calc_link_xpath):
        link_role_href = linkrole.get(role_xpath)
        store[link_role_href] = {}
        for arc in linkrole.iterfind(calc_arc_xpath):
            label_from = linkrole.find(
                calc_loc_xpath + lab_attr_xpath % arc.get(from_xpath)
            )
            label_to = linkrole.find(
                calc_loc_xpath + lab_attr_xpath % arc.get(to_xpath)
            )
            parent = label_from.get(href_xpath).split("#")[-1]
            child = label_to.get(href_xpath).split("#")[-1]

            if parent not in store[link_role_href]:
                store[link_role_href][parent] = []
            store[link_role_href][parent].append((child, arc.get("weight")))

    for linkrole, totals in store.items():
        for total, sum_elements in totals.items():
            sum_elements.sort(key=lambda tup: tup[0])

    return store


def dup_calcs(elem):
    """Return all duplicate calculation relationships in the given element."""
    def add_warning(total, warnings):
        if total in warnings:
            warnings[total] += 1
        else:
            warnings[total] = 0

        return warnings

    store = get_calcs(elem)
    warnings = {}
    base_calcs = {}
    for linkrole in store:
        for total in store[linkrole]:
            if total in base_calcs:
                new_children = set(store[linkrole][total])
                totals = base_calcs[total]
                if new_children in totals:
                    warnings = add_warning(total, warnings)
                else:
                    set_new_children = set(new_children)
                    found = False
                    for foot in totals:
                        set_old_children = set(foot)
                        if set_new_children.issubset(set_old_children):
                            warnings = add_warning(total, warnings)
                            found = True
                            break
                        elif set_new_children.issuperset(set_old_children):
                            warnings = add_warning(total, warnings)
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
    context_ref = ".//{{{0}}}{1}[@contextRef='{2}']"
    for link_role, total_elems in calcs.items():
        for total_elem, line_items in total_elems.items():
            total_split = total_elem.split("_", 1)
            namespace = ".//{{{0}}}".format(nsmap[total_split[0]])
            for total in elem.iterfind(namespace + total_split[-1]):
                value = Decimal(total.text)
                cont = total.get("contextRef")
                calculated_total = 0
                changed = False
                for line_item in line_items:
                    line_item_split = line_item[0].split("_", 1)
                    ns = (nsmap[line_item_split[0]], line_item_split[-1], cont)
                    new = elem.find(context_ref.format(*ns))
                    if new is not None and new.text is not None:
                        changed = True
                        weight = line_item[1]
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
    labels = get_labels(elem)
    short_labels = {}
    for label, label_types in labels.items():
        short_labels[label.split("#")[-1]] = label_types
    for calc in calcs:
        standard_lab = ""
        if calc[1] in short_labels:
            standard_lab = short_labels[calc[1]][role_label]
        calc.insert(1, standard_lab)

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

    for linkbase_ref in elem.iterfind(linkbase_refs_xpath):
        match = sort_reg.search(linkbase_ref.text)
        sort = match.group(1)
        link_def = match.group(2)
        new_sort = sort
        if sort == dei:
            new_sort = "00090"
        elif face_par.search(sort):
            new_sort = "{0}0{1}".format(sort[:3], sort[-1:])
        elif text_block.search(sort):
            new_sort = "{0}0{1}".format(sort[:3], sort[:1])
        elif face_fin.search(sort) or eights.search(sort):
            new_sort = "{0}0".format(sort)
        elif level_four.search(sort):
            code = int(sort[-1:]) + 1
            if code < 10:
                new_sort = "{0}0{1}".format(sort[:-1], str(code))
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
        for link_ref in elem.iterfind(link_refs_xpath):
            old_path = link_ref.get(href_attr_xpath)
            match = filename.search(old_path)
            new_path = "{0}current_taxonomy{1}".format(
                match.group(1),
                match.group(3)
            )
            link_ref.set(href_attr_xpath, new_path)
            log.append((old_path, new_path))
        base = match.group(1) + match.group(2)
        log.append(("{0}.xsd".format(base),
                    "{0}current_taxonomy.xsd".format(match.group(1))))
        log.append(("{0}.xml".format(base), "*Deleted*"))
    else:
        links = ["loc"]
        if linkbase == "linkbase":
            links.append("roleRef")
        for link in links:
            xpath = ".//{http://www.xbrl.org/2003/linkbase}%s" % link
            for link_ref in elem.iterfind(xpath):
                match = path.search(link_ref.get(href_attr_xpath))
                if match:
                    xsd = "{0}current_taxonomy{1}".format(
                        match.group(1),
                        match.group(3)
                    )
                    link_ref.set(href_attr_xpath, xsd + match.group(4))

    return log


def retrieve_base(elem):
    """Return the base taxonomy from the provided schema element."""
    version = ""
    ugt = re.compile("(us-gaap-\d{4}-\d{2}-\d{2})\.xsd$")

    for schema in elem.iterfind("{http://www.w3.org/2001/XMLSchema}import"):
        location = ugt.search(schema.get("schemaLocation"))
        if location:
            version = location.group(1)
            break

    return version


def get_link_roles(elem):
    """Return all extension link role URIs found in the given element."""
    log = []
    role_type_xpath = ".//{http://www.xbrl.org/2003/linkbase}roleType"

    for link_role in elem.iterfind(role_type_xpath):
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
            for link_role in value["root"].iterfind(xpaths[key]):
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
