#!/usr/bin/env python

import namespace
import sys
import re
import os
from operator import itemgetter
import csv
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets
from ui_thinX import Ui_MainWindow
import xbrl


class ThinX(QtWidgets.QMainWindow):
    """The main app class. Handles the GUI and various XBRL utilities."""
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__init_statusbar()
        self.__init_connections()
        self.about()
        self.filename = ""
        self.unit_config_file = "units.ini"

    def __init_connections(self):
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionClose.triggered.connect(self.close)
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionLinkRoles.triggered.connect(self.link_role)
        self.ui.actionLabels.triggered.connect(self.labels)
        self.ui.actionConsolidateLabels.triggered.connect(self.redundant_labels)
        self.ui.actionConcepts.triggered.connect(self.concepts)
        self.ui.actionCalculations.triggered.connect(self.calculations)
        self.ui.actionContexts.triggered.connect(self.contexts)
        self.ui.actionTwoDayContexts.triggered.connect(self.two_day_contexts)
        self.ui.actionUnits.triggered.connect(self.units)
        self.ui.actionInconsistencies.triggered.connect(self.inconsistencies)
        self.ui.actionMerrillBridgePrep.triggered.connect(self.bridge_prep)
        self.ui.actionMerrillBridgeSort.triggered.connect(self.bridge_sort)

    def get_version(self):
        try:
            f = open("_version.py")
        except EnvironmentError:
            return None
        for line in f.readlines():
            mo = re.match("__version__ = \"([^']+)\"", line)
            if mo:
                ver = mo.group(1)
                return ver
        return None

    def __init_statusbar(self):
        self.status = QtWidgets.QLabel()
        self.reset_status()
        self.statusBar().addPermanentWidget(self.status)

    def reset_status(self):
        """Resets the text in the status bar."""
        self.status.setText("Open an Instance Document to Begin ")

    def open_fail(self, instance, file_type=None):
        """Logs a file that failed to open to the status bar."""
        file_types = {
            "xsd": "Schema",
            "pre": "Presentation Linkbase",
            "def": "Definition Linkbase",
            "cal": "Calculation Linkbase",
            "lab": "Label Linkbase"
        }
        if file_type in file_types:
            self.status.setText(
                "Failed to Open "
                + file_types[file_type]
                + " of: "
                + instance
                + " "
            )
        else:
            self.status.setText("Failed to Open: " + instance + " ")

    def open(self):
        """Prompts the user to open an XBRL instance document and stores the
        file path in self.filename.

        """
        self.ui.textLog.clear()
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            filter="Instance Document (*.XML *.XBRL)"
        )[0]
        if self.filename != "":
            self.status.setText(self.filename)
        else:
            self.reset_status()

    def close(self):
        """Closes any open files and resets the interface."""
        self.filename = ""
        self.reset_status()
        self.ui.textLog.clear()
        self.about()

    def about(self):
        """Displays project information."""
        self.ui.textLog.clear()
        self.ui.textLog.append(
            "<html><head/><body><br><p align=\"center\" style=\"font-size:24pt;"
            " font-weight:600;\">thinX</p><p align=\"center\"><span style=\" "
            "font-size:10pt;\">thinX is an open source XBRL toolkit developed "
            "and maintained<br>by Austin M. Matherne and released under the "
            "WTFPL.</span></p><p align=\"center\">https://github.com/Austin"
            "Matherne/thinX</p><p align=\"center\" style=\"font-size:8pt;\">"
            + str(self.get_version()) + "</p></body></html>"
        )

    def link_role(self):
        """Find, report, and delete any inactive link roles."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                xsd = xbrl.get_linkbase(self.filename, "xsd")
                pre_linkbase = xbrl.get_linkbase(self.filename, "pre")
                def_linkbase = xbrl.get_linkbase(self.filename, "def")
                cal_linkbase = xbrl.get_linkbase(self.filename, "cal")
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                xsd_tree = namespace.parse_xmlns(xsd)
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                pre_tree = namespace.parse_xmlns(pre_linkbase)
            except:
                self.open_fail(self.filename, "pre")
                return

            try:
                def_tree = namespace.parse_xmlns(def_linkbase)
            except:
                self.open_fail(self.filename, "def")
                return

            try:
                cal_tree = namespace.parse_xmlns(cal_linkbase)
            except:
                self.open_fail(self.filename, "cal")
                return

            xsd_root = xsd_tree.getroot()
            linkbases = {"pre": pre_tree.getroot(),
                         "def": def_tree.getroot(),
                         "cal": cal_tree.getroot()}

            link_roles = xbrl.get_link_roles(xsd_root)
            active_link_roles = xbrl.get_active_link_roles(linkbases)
            log = xbrl.compare_link_roles(link_roles, active_link_roles)

            if not log:
                self.status.setText("No Unused Link Roles Found in File ")
            else:
                xbrl.delete_link_roles(xsd_root, log)
                namespace.fixup_xmlns(xsd_root)
                xsd_tree.write(xsd, xml_declaration=True)
                self.ui.textLog.append("<strong>Unused Link Roles:</strong>")
                for role in log:
                    self.ui.textLog.append(role)
                self.ui.textLog.append("")
                self.status.setText(
                    "The Above Unused Link Roles Have Been Removed "
                )

    def labels(self):
        """Removes and logs labels which are not in use."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                pre_linkbase = xbrl.get_linkbase(self.filename, "pre")
                lab_linkbase = xbrl.get_linkbase(self.filename, "lab")
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                pre_tree = namespace.parse_xmlns(pre_linkbase)
            except:
                self.open_fail(self.filename, "pre")
                return

            try:
                lab_tree = namespace.parse_xmlns(lab_linkbase)
            except:
                self.open_fail(self.filename, "lab")
                return

            pre_root = pre_tree.getroot()
            lab_root = lab_tree.getroot()

            log = xbrl.clean_labels(lab_root, pre_root)
            if not log:
                self.status.setText("No Unused Labels Found in File ")
            else:
                namespace.fixup_xmlns(lab_root)
                lab_tree.write(lab_linkbase, xml_declaration=True)
                self.status.setText(
                    "The Above Unreferenced Labels Have Been Removed "
                )
                for element, labels in log.items():
                    self.ui.textLog.append(
                        "<strong>"
                        + element.rsplit("#")[-1]
                        + ":</strong>"
                    )
                    for label_type, label in labels.items():
                        self.ui.textLog.append(
                            label_type.rsplit("/")[-1]
                            + ": "
                            + label
                        )

    def redundant_labels(self):
        """Removes and logs labels which are redundant."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                pre_linkbase = xbrl.get_linkbase(self.filename, "pre")
                lab_linkbase = xbrl.get_linkbase(self.filename, "lab")
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                pre_tree = namespace.parse_xmlns(pre_linkbase)
            except:
                self.open_fail(self.filename, "pre")
                return

            try:
                lab_tree = namespace.parse_xmlns(lab_linkbase)
            except:
                self.open_fail(self.filename, "lab")
                return

            pre_root = pre_tree.getroot()
            lab_root = lab_tree.getroot()

            log = xbrl.redundant_labels(lab_root, pre_root)
            if not log:
                self.status.setText("No Redundant Labels Found in File ")
            else:
                namespace.fixup_xmlns(pre_root)
                namespace.fixup_xmlns(lab_root)
                pre_tree.write(pre_linkbase, xml_declaration=True)
                lab_tree.write(lab_linkbase, xml_declaration=True)
                self.status.setText(
                    "The Above Redundant Labels Have Been Removed "
                )
                for element, labels in log.items():
                    self.ui.textLog.append(
                        "<strong>"
                        + element.rsplit("#")[-1]
                        + ":</strong>"
                    )
                    for label_type, label in labels.items():
                        self.ui.textLog.append(
                            label_type.rsplit("/")[-1]
                            + " > "
                            + label.rsplit("/")[-1]
                        )

    def concepts(self):
        """Removes and logs extension concepts which are not in use."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                xsd = xbrl.get_linkbase(self.filename, "xsd")
                pre_linkbase = xbrl.get_linkbase(self.filename, "pre")
                def_linkbase = xbrl.get_linkbase(self.filename, "def")
                cal_linkbase = xbrl.get_linkbase(self.filename, "cal")
                lab_linkbase = xbrl.get_linkbase(self.filename, "lab")
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                xsd_tree = namespace.parse_xmlns(xsd)
            except:
                self.open_fail(self.filename, "xsd")
                return

            try:
                pre_tree = namespace.parse_xmlns(pre_linkbase)
            except:
                self.open_fail(self.filename, "pre")
                return

            try:
                def_tree = namespace.parse_xmlns(def_linkbase)
            except:
                self.open_fail(self.filename, "def")
                return

            try:
                cal_tree = namespace.parse_xmlns(cal_linkbase)
            except:
                self.open_fail(self.filename, "cal")
                return

            try:
                lab_tree = namespace.parse_xmlns(lab_linkbase)
            except:
                self.open_fail(self.filename, "lab")
                return

            xsd_root = xsd_tree.getroot()
            pre_root = pre_tree.getroot()
            def_root = def_tree.getroot()
            cal_root = cal_tree.getroot()
            lab_root = lab_tree.getroot()

            log = xbrl.clean_concepts(
                xsd_root,
                pre_root,
                def_root,
                cal_root,
                lab_root,
                xsd.split("/")[-1]
            )
            if not log:
                self.status.setText("No Unused Concepts Found in File ")
            else:
                namespace.fixup_xmlns(xsd_root)
                xsd_tree.write(xsd, xml_declaration=True)
                self.status.setText(
                    "The Above Unreferenced Concepts Have Been Removed "
                )
                self.ui.textLog.append("<strong>Unused Concepts:</strong>")
                for concept in log:
                    self.ui.textLog.append(concept)

    def calculations(self):
        """Displays duplicate calculations found in the corresponding
        calculation linkbase of self.filename.

        """
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                calc_linkbase = xbrl.get_linkbase(self.filename, "cal")
            except:
                self.open_fail(self.filename, "cal")
                return
            tree = namespace.parse_xmlns(calc_linkbase)
            root = tree.getroot()
            log = xbrl.dup_calcs(root)
            if not log:
                self.status.setText("No Duplicate Calculations Found ")
            else:
                self.status.setText(
                    "Duplicate Calculations For The Above Total Concepts Have "
                    "Been Found "
                )
                self.ui.textLog.append(
                    "<strong>Duplicate Calculations:</strong>"
                )
                for calc, mutliples in log.items():
                    if mutliples > 0:
                        self.ui.textLog.append(calc + " *" + str(mutliples + 1))
                    else:
                        self.ui.textLog.append(calc)

    def contexts(self):
        """Removes unused contexts from self.filename."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                tree = namespace.parse_xmlns(self.filename)
            except:
                self.open_fail(self.filename)
                return

            root = tree.getroot()
            log = xbrl.clean_contexts(root)
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            if not log:
                self.status.setText("No Unused Contexts Found in File ")
            else:
                self.status.setText(
                    "The Above Unreferenced Contexts Have Been Removed "
                )
                self.ui.textLog.append("<strong>Unused Contexts:</strong>")
                for item in log:
                    self.ui.textLog.append(item)

    def two_day_contexts(self):
        """Report two day contexts."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                tree = namespace.parse_xmlns(self.filename)
            except:
                self.open_fail(self.filename)
                return

            root = tree.getroot()
            log = xbrl.two_day_contexts(root)
            if not log:
                self.status.setText("No Two Day Contexts Found in File ")
            else:
                self.status.setText(
                    "The Above Two Day Contexts Were Found "
                )
                self.ui.textLog.append("<strong>Two Day Contexts:</strong>")
                for item in log:
                    self.ui.textLog.append(item)

    def units(self):
        """Adds the namespaces supplied in unit_config_file to self.filename
        and swaps out all measures in self.filename that are also in the
        unit_config_file. The measure that is swapped in also uses its
        matching namespace and prefix from the unit_config_file.

        """
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            fixed = False
            logs = []
            try:
                tree = namespace.parse_xmlns(self.filename)
            except:
                self.open_fail(self.filename)
                return

            root = tree.getroot()
            registries = xbrl.get_units(self.unit_config_file, self.filename)
            prefixes = []
            for key, registry in registries.items():
                prefix = "xmlns:" + registry["Prefix"]
                prefixes.append(prefix)
                ns = registry["Namespace"]
                measures = registry["Measures"]
                log = xbrl.add_namespace(root, prefix, ns, measures)
                if log:
                    logs.append(log)
                    fixed = True
            check = xbrl.unknown_measures(
                root,
                self.unit_config_file,
                self.filename
            )
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            if fixed:
                self.status.setText("XBRL International Units Registry ")
                self.ui.textLog.append(
                    "<strong>The Following Measures Have Been Modified:"
                    "</strong>"
                )
                for dictionary in logs:
                    for item in dictionary:
                        self.ui.textLog.append(item + " > " + dictionary[item])
                self.ui.textLog.append("<br>")
            else:
                self.status.setText("No Units Found to Fix ")

            if len(check) > 0:
                self.ui.textLog.append(
                    "<strong>The Following Measures Are Not Part Of Any Known "
                    "Units Database:</strong>"
                )
                for measure in check:
                    self.ui.textLog.append(measure)

    def inconsistencies(self):
        """Report calculation inconsistencies."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                xsd = xbrl.get_linkbase(self.filename, "xsd")
                cal_linkbase = xbrl.get_linkbase(self.filename, "cal")
                lab_linkbase = xbrl.get_linkbase(self.filename, "lab")
            except:
                self.open_fail(self.filename, "xsd")
                return

            tree = namespace.parse_xmlns(self.filename)
            xsd_tree = namespace.parse_xmlns(xsd)
            cal_tree = namespace.parse_xmlns(cal_linkbase)
            lab_tree = namespace.parse_xmlns(lab_linkbase)
            root = tree.getroot()
            xsd_root = xsd_tree.getroot()
            cal_root = cal_tree.getroot()
            lab_root = lab_tree.getroot()
            calcs = xbrl.get_calcs(cal_root)
            log = xbrl.calc_values(root, calcs)
            if not log:
                self.status.setText("No Calculation Inconsistencies Found ")
            else:
                log = xbrl.insert_labels(lab_root, log)
                for calc in log:
                    calc[0] = xbrl.link_role_def(xsd_root, calc[0])
                    calc[2] = calc[2].replace("_", ":")

                log = sorted(log, key=itemgetter(0, 1, 2, 3))
                self.ui.textLog.append(
                    "<strong>Calculation Inconsistencies:</strong>"
                )
                link_roles = {}
                output = []
                for row in log:
                    sort = row[0].split(" ", 1)[0]
                    if sort in link_roles:
                        if row[2] in link_roles[sort]:
                            link_roles[sort][row[2]] += 1
                        else:
                            link_roles[sort][row[2]] = 1
                    else:
                        link_roles[sort] = {row[2]: 1}
                for link_role, totals in link_roles.items():
                    for total, value in totals.items():
                        output.append(link_role + " - " + total + " *" + str(value))
                output.sort()
                log.insert(0, ["RoleDefinition",
                         "ElementLabel",
                         "Element",
                         "ContextId",
                         "Value",
                         "CalculatedValue"])
                out_file = self.filename.rsplit(".", 1)[0] + "-calc.csv"
                with open(out_file, 'w', newline='') as f:
                    writer = csv.writer(f, dialect='excel', delimiter=',')
                    writer.writerows(log)
                for row in output:
                    self.ui.textLog.append(row)
                self.status.setText(" ".join([
                    "Calculation Inconsistency Report Saved to",
                    out_file,
                    ""
                ]))

    def bridge_prep(self):
        """Prep taxonomy for import into Merrill Bridge."""
        comment = ('<?xml version="1.0" encoding="utf-8"?>\n<!--XBRL document '
                   'created with Crossfire by Rivet Software version 5.7.123.0 '
                   'http://www.rivetsoftware.com-->\n<!--Based on XBRL 2.1-->\n'
                   '<!--Created on: 2/13/2014 12:47:00 PM-->\n<!--Modified on: '
                   '2/13/2014 12:48:00 PM-->\n')

        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            self.link_role()
            try:
                schema = xbrl.get_linkbase(self.filename, "xsd")
                pres = xbrl.get_linkbase(self.filename, "pre")
                defs = xbrl.get_linkbase(self.filename, "def")
                calc = xbrl.get_linkbase(self.filename, "cal")
                labs = xbrl.get_linkbase(self.filename, "lab")
                linkbases = [schema, pres, defs, calc, labs]
            except:
                self.open_fail(self.filename, "xsd")
                return
            path = re.compile("^(.+)\d{8}([\.-abcdeflmprsx]{4,8})$")
            name = "current_taxonomy"
            os.remove(self.filename)
            for linkbase in linkbases:
                tree = namespace.parse_xmlns(linkbase)
                root = tree.getroot()
                if linkbase == schema:
                    log = xbrl.link_role_sort(root)
                    ns_change = xbrl.remove_namespace_date(root)
                    refs = xbrl.rename_refs(root, "xsd")
                    base = xbrl.retrieve_base(root)
                elif linkbase == labs:
                    lab_log = xbrl.rename_refs(root, "labs")
                else:
                    ref_log = xbrl.rename_refs(root, "linkbase")
                namespace.fixup_xmlns(root)
                content = ET.tostring(root, encoding="unicode")
                match = path.search(linkbase)
                new_name = match.group(1) + name + match.group(2)
                f = open(new_name, 'w', encoding="utf8")
                f.write(comment + content)
                f.close()
                os.remove(linkbase)
            if log:
                self.ui.textLog.append("<strong>Sort Codes:</strong>")
                for link in log:
                    self.ui.textLog.append(link[0] + " > " + link[1])
                self.ui.textLog.append("")
            self.ui.textLog.append("<strong>Files:</strong>")
            for ref in refs:
                self.ui.textLog.append(ref[0] + " > " + ref[1])
            self.ui.textLog.append("<br><strong>Namespace:</strong>")
            self.ui.textLog.append(ns_change[0] + " > " + ns_change[1])
            self.ui.textLog.append("<br><strong>Base Taxonomy:</strong>")
            self.ui.textLog.append(base)
            self.status.setText("Ready for Bridge ")

    def bridge_sort(self):
        """Update link role sorting for Merrill Bridge."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            self.ui.textLog.clear()
            try:
                schema = xbrl.get_linkbase(self.filename, "xsd")
            except:
                self.open_fail(self.filename, "xsd")
                return
            tree = namespace.parse_xmlns(schema)
            root = tree.getroot()
            log = xbrl.link_role_sort(root)
            namespace.fixup_xmlns(root)
            tree.write(schema, xml_declaration=True)
            self.ui.textLog.append("<strong>Sort Codes:</strong>")
            for link in log:
                self.ui.textLog.append(link[0] + " > " + link[1])
            self.status.setText("Ready for Compare ")

def main():
    """Launches Qt and creates an instance of ThinX."""
    app = QtWidgets.QApplication(sys.argv)
    window = ThinX()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
