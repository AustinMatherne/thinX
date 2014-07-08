#!/usr/bin/env python

import sys
import re
import os
from operator import itemgetter
import csv
from lxml import etree
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
        self.ui.actionConsolidateLabels.triggered.connect(self.redundant)
        self.ui.actionStandardLabels.triggered.connect(self.standard_labels)
        self.ui.actionConcepts.triggered.connect(self.concepts)
        self.ui.actionCalculations.triggered.connect(self.calculations)
        self.ui.actionContexts.triggered.connect(self.contexts)
        self.ui.actionTwoDayContexts.triggered.connect(self.two_day_contexts)
        self.ui.actionUnits.triggered.connect(self.units)
        self.ui.actionInconsistencies.triggered.connect(self.inconsistencies)
        self.ui.actionMerrillBridgePrep.triggered.connect(self.bridge_prep)
        self.ui.actionMerrillBridgeSort.triggered.connect(self.bridge_sort)

    def __init_statusbar(self):
        self.status = QtWidgets.QLabel()
        self.reset_status()
        self.statusBar().addPermanentWidget(self.status)

    def get_version(self):
        """Retrieves the version number of thinX."""
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
            self.status.setText("Failed to Open {0} of: {1} ".format(
                file_types[file_type], instance
            ))
        else:
            self.status.setText("Failed to Open: {0} ".format(instance))

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
            "<html><head/><body><br><p align=\"center\" "
            "style=\"font-size:24pt; font-weight:600;\">thinX</p><p "
            "align=\"center\"><span style=\"font-size:10pt;\">thinX is an open"
            " source XBRL toolkit developed and maintained<br>by Austin M. "
            "Matherne and released under the WTFPL.</span></p><p "
            "align=\"center\">https://github.com/AustinMatherne/thinX</p><p "
            "align=\"center\" style=\"font-size:8pt;\">{0}</p></body></html>"
            .format(str(self.get_version()))
        )

    def link_role(self):
        """Find, report, and delete any inactive link roles."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd", "pre", "def", "cal"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        link_roles = xbrl.get_link_roles(linkbases["xsd"]["root"])
        active_link_roles = xbrl.get_active_link_roles(linkbases)
        log = xbrl.compare_link_roles(link_roles, active_link_roles)

        if not log:
            self.status.setText("No Unused Link Roles Found in File ")
        else:
            xbrl.delete_link_roles(linkbases["xsd"]["root"], log)
            linkbases["xsd"]["tree"].write(
                linkbases["xsd"]["filename"],
                xml_declaration=True
            )
            self.ui.textLog.append("<strong>Unused Link Roles:</strong>")
            for role in log:
                self.ui.textLog.append(role)
            self.ui.textLog.append("")
            self.status.setText(
                "The Above Unused Link Roles Have Been Removed "
            )

    def labels(self):
        """Removes and logs labels which are not in use."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd", "pre", "lab"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.clean_labels(
            linkbases["lab"]["root"],
            linkbases["pre"]["root"]
        )
        if not log:
            self.status.setText("No Unused Labels Found in File ")
        else:
            linkbases["lab"]["tree"].write(
                linkbases["lab"]["filename"],
                xml_declaration=True
            )
            self.status.setText(
                "The Above Unreferenced Labels Have Been Removed "
            )
            for element, labels in log.items():
                self.ui.textLog.append(
                    "<strong>{0}:</strong>".format(element.rsplit("#")[-1])
                )
                for label_type, label in labels.items():
                    self.ui.textLog.append(
                        "{0}: {1}".format(label_type.rsplit("/")[-1], label)
                    )

    def redundant(self):
        """Removes and logs labels which are redundant."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd", "pre", "lab"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.redundant_labels(
            linkbases["lab"]["root"],
            linkbases["pre"]["root"]
        )
        if not log:
            self.status.setText("No Redundant Labels Found in File ")
        else:
            linkbases["pre"]["tree"].write(
                linkbases["pre"]["filename"],
                xml_declaration=True
            )
            linkbases["lab"]["tree"].write(
                linkbases["lab"]["filename"],
                xml_declaration=True
            )
            self.status.setText(
                "The Above Redundant Labels Have Been Removed "
            )
            for element, labels in log.items():
                self.ui.textLog.append(
                    "<strong>{0}:</strong>".format(element.rsplit("#")[-1])
                )
                for label_type, label in labels.items():
                    self.ui.textLog.append(
                        "{0} > {1}".format(
                            label_type.rsplit("/")[-1],
                            label.rsplit("/")[-1]
                        )
                    )

    def standard_labels(self):
        """Removes and logs standard labels which are from a base taxonomy."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        try:
            linkbases = xbrl.open_linkbases(self.filename, ["lab"])
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.remove_standard_labels(linkbases["lab"]["root"])
        if not log:
            self.status.setText("No Standard Labels Found in File ")
        else:
            linkbases["lab"]["tree"].write(
                linkbases["lab"]["filename"],
                xml_declaration=True
            )
            self.status.setText(
                "The Above Standard Labels Have Been Removed "
            )
            for element, labels in log.items():
                self.ui.textLog.append(
                    "<strong>{0}:</strong>".format(element.rsplit("#")[-1])
                )
                for label_type, label in labels.items():
                    self.ui.textLog.append(
                        "{0} > {1}".format(
                            label_type.rsplit("/")[-1],
                            label.rsplit("/")[-1]
                        )
                    )

    def concepts(self):
        """Removes and logs extension concepts which are not in use."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd", "pre", "def", "cal", "lab"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.clean_concepts(linkbases)
        if not log:
            self.status.setText("No Unused Concepts Found in File ")
        else:
            linkbases["xsd"]["tree"].write(
                linkbases["xsd"]["filename"],
                xml_declaration=True
            )
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
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["cal"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.dup_calcs(linkbases["cal"]["root"])
        if not log:
            self.status.setText("No Duplicate Calculations Found ")
        else:
            self.status.setText(
                "Duplicate Calculations For The Above Total Concepts Have "
                "Been Found "
            )
            self.ui.textLog.append("<strong>Duplicate Calculations:</strong>")
            for calc, multiple in log.items():
                if multiple > 0:
                    self.ui.textLog.append(
                        "{0} *{1}".format(calc, str(multiple + 1)))
                else:
                    self.ui.textLog.append(calc)

    def contexts(self):
        """Removes unused contexts from self.filename."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        try:
            tree = etree.parse(self.filename)
        except:
            self.open_fail(self.filename)
            return

        root = tree.getroot()
        log = xbrl.clean_contexts(root)
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
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        try:
            tree = etree.parse(self.filename)
        except:
            self.open_fail(self.filename)
            return

        root = tree.getroot()
        log = xbrl.two_day_contexts(root)
        if not log:
            self.status.setText("No Two Day Contexts Found in File ")
        else:
            self.status.setText("The Above Two Day Contexts Were Found ")
            self.ui.textLog.append("<strong>Two Day Contexts:</strong>")
            for item in log:
                self.ui.textLog.append(item)

    def units(self):
        """Adds the namespaces supplied in unit_config_file to self.filename
        and swaps out all measures in self.filename that are also in the
        unit_config_file. The measure that is swapped in also uses its
        matching namespace and prefix from the unit_config_file.

        """
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        fixed = False
        logs = []
        try:
            tree = etree.parse(self.filename)
        except:
            self.open_fail(self.filename)
            return

        root = tree.getroot()
        registry = xbrl.get_units(self.unit_config_file, self.filename)
        new_root, log = xbrl.add_namespace(root, registry)
        if log:
            logs.append(log)
            fixed = True
        check = xbrl.unknown_measures(
            new_root,
            self.unit_config_file,
            self.filename
        )
        tree._setroot(new_root)
        tree.write(self.filename, xml_declaration=True)
        if fixed:
            self.status.setText("XBRL International Units Registry ")
            self.ui.textLog.append(
                "<strong>The Following Measures Have Been Modified: </strong>"
            )
            for dictionary in logs:
                for item in dictionary:
                    self.ui.textLog.append(
                        "{0} > {1}".format(item, dictionary[item])
                    )
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
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd", "pre", "def", "cal", "lab"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        try:
            tree = etree.parse(self.filename)
        except:
            self.open_fail(self.filename)
            return

        root = tree.getroot()
        calcs = xbrl.get_calcs(linkbases["cal"]["root"])
        log = xbrl.calc_values(root, calcs)
        if not log:
            self.status.setText("No Calculation Inconsistencies Found ")
        else:
            log = xbrl.insert_labels(linkbases["lab"]["root"], log)
            for calc in log:
                calc[0] = xbrl.link_role_def(linkbases["xsd"]["root"], calc[0])
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
                    line = "{0} - {1} *{2}".format(
                        link_role,
                        total,
                        str(value)
                    )
                    output.append(line)
            output.sort()
            log.insert(0, ["RoleDefinition",
                           "ElementLabel",
                           "Element",
                           "ContextId",
                           "Value",
                           "CalculatedValue"])
            out_file = "{0}-calc.csv".format(self.filename.rsplit(".", 1)[0])
            with open(out_file, 'w', newline='') as f:
                writer = csv.writer(f, dialect='excel', delimiter=',')
                writer.writerows(log)
            for row in output:
                self.ui.textLog.append(row)
            self.status.setText(
                "Calculation Inconsistency Report Saved to {0} ".format(
                    out_file
                )
            )

    def bridge_prep(self):
        """Prep taxonomy for import into Merrill Bridge."""
        comment = ('<?xml version="1.0" encoding="utf-8"?>\n<!--XBRL document '
                   'created with Merrill Bridge Powered by Crossfire 5.9.112.0'
                   ' -->\n<!--Based on XBRL 2.1-->\n<!--Created on: 5/14/2014 '
                   '3:24:21 PM-->\n<!--Modified on: 5/14/2014 3:24:21 PM-->\n')

        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        self.link_role()
        files = ["xsd", "pre", "def", "cal", "lab"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        path = re.compile("^(.+)\d{8}([\.-abcdeflmprsx]{4,8})$")
        name = "current_taxonomy"
        os.remove(self.filename)
        for key, value in linkbases.items():
            if key == "xsd":
                log = xbrl.link_role_sort(value["root"])
                refs = xbrl.rename_refs(value["root"], "xsd")
                base = xbrl.retrieve_base(value["root"])
                value["root"], ns_change = xbrl.remove_namespace_date(
                    value["root"]
                )
            elif key == "lab":
                xbrl.rename_refs(value["root"], "lab")
            else:
                xbrl.rename_refs(value["root"], "linkbase")
            content = etree.tostring(value["root"], encoding="unicode")
            match = path.search(value["filename"])
            new_name = match.group(1) + name + match.group(2)
            f = open(new_name, 'w', encoding="utf8")
            f.write(comment + content)
            f.close()
            os.remove(value["filename"])
        if log:
            self.ui.textLog.append("<strong>Sort Codes:</strong>")
            for link in log:
                self.ui.textLog.append("{0} > {1}".format(link[0], link[1]))
            self.ui.textLog.append("")
        self.ui.textLog.append("<strong>Files:</strong>")
        for ref in refs:
            self.ui.textLog.append("{0} > {1}".format(ref[0], ref[1]))
        self.ui.textLog.append("<br><strong>Namespace:</strong>")
        self.ui.textLog.append("{0} > {1}".format(ns_change[0], ns_change[1]))
        self.ui.textLog.append("<br><strong>Base Taxonomy:</strong>")
        self.ui.textLog.append(base)
        self.status.setText("Ready for Bridge ")

    def bridge_sort(self):
        """Update link role sorting for Merrill Bridge."""
        if not self.filename:
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return

        self.ui.textLog.clear()
        files = ["xsd"]
        try:
            linkbases = xbrl.open_linkbases(self.filename, files)
        except Exception as e:
            self.open_fail(self.filename, e.value)
            return

        log = xbrl.link_role_sort(linkbases["xsd"]["root"])
        linkbases["xsd"]["tree"].write(
            linkbases["xsd"]["filename"],
            xml_declaration=True
        )
        self.ui.textLog.append("<strong>Sort Codes:</strong>")
        for link in log:
            self.ui.textLog.append("{0} > {1}".format(link[0], link[1]))
        self.status.setText("Ready for Compare ")


def main():
    """Launches Qt and creates an instance of ThinX."""
    app = QtWidgets.QApplication(sys.argv)
    window = ThinX()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
