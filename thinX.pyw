#!/usr/bin/env python

import namespace
import sys
import re
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
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionUnits.triggered.connect(self.units)
        self.ui.actionContexts.triggered.connect(self.contexts)
        self.ui.actionCalculations.triggered.connect(self.calculations)
        self.ui.actionLabels.triggered.connect(self.labels)

    def __init_statusbar(self):
        self.status = QtWidgets.QLabel()
        self.reset_status()
        self.statusBar().addPermanentWidget(self.status)

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

    def about(self):
        """Displays project information."""
        self.ui.textLog.clear()
        self.ui.textLog.append(
            "<html><head/><body><p align=\"center\" style=\"font-size:24pt; "
            "font-weight:600;\">thinX</p><p align=\"center\"><span style=\" "
            "font-size:10pt;\">thinX is an open source XBRL toolkit developed "
            "and maintained<br>by Austin M. Matherne and released under the "
            "WTFPL.</span></p><p align=\"center\">https://github.com/Austin"
            "Matherne/thinX</p><p align=\"center\" style=\"font-size:8pt;\">"
            + str(self.get_version()) + "</p></body></html>"
        )

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
            fixed = False
            logs = []
            try:
                tree = namespace.parse_xmlns(self.filename)
            except:
                self.ui.textLog.clear()
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
            self.ui.textLog.clear()
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
                    "Units Database:<br>If You Believe They Are Legitimate, "
                    "Please Contact Austin M. Matherne.</strong>"
                )
                for measure in check:
                    self.ui.textLog.append(measure)

    def contexts(self):
        """Removes unused contexts from self.filename."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            try:
                tree = namespace.parse_xmlns(self.filename)
            except:
                self.ui.textLog.clear()
                self.open_fail(self.filename)
                return

            root = tree.getroot()
            log = xbrl.clean_contexts(root)
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            self.ui.textLog.clear()
            if not log:
                self.status.setText("No Unused Contexts Found in File ")
            else:
                self.status.setText(
                    "The Above Unreferenced Contexts Have Been Removed "
                )
                for item in log:
                    self.ui.textLog.append(item)

    def labels(self):
        """Removes and logs labels which are not in use."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing "
            )
            return
        else:
            try:
                pre_linkbase = xbrl.get_linkbase(self.filename, "pre")
                lab_linkbase = xbrl.get_linkbase(self.filename, "lab")
            except:
                self.ui.textLog.clear()
                self.open_fail(self.filename, "xsd")
                return

            try:
                pre_tree = namespace.parse_xmlns(pre_linkbase)
            except:
                self.ui.textLog.clear()
                self.open_fail(self.filename, "pre")
                return

            try:
                lab_tree = namespace.parse_xmlns(lab_linkbase)
            except:
                self.ui.textLog.clear()
                self.open_fail(self.filename, "lab")
                return

            pre_root = pre_tree.getroot()
            lab_root = lab_tree.getroot()

            log = xbrl.clean_labels(lab_root, pre_root)
            self.ui.textLog.clear()
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
                        + "</strong>"
                    )
                    for label_type, label in labels.items():
                        self.ui.textLog.append(
                            label_type.rsplit("/")[-1]
                            + ": "
                            + label
                        )

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
            try:
                calc_linkbase = xbrl.get_linkbase(self.filename, "cal")
            except:
                self.ui.textLog.clear()
                self.open_fail(self.filename, "cal")
                return

            tree = namespace.parse_xmlns(calc_linkbase)
            root = tree.getroot()
            log = xbrl.dup_calcs(root)
            self.ui.textLog.clear()
            if not log:
                self.status.setText("No Duplicate Calculations Found ")
            else:
                self.status.setText(
                    "Duplicate Calculations For The Above Total Concepts Have "
                    "Been Found "
                )
                for calc, mutliples in log.items():
                    if mutliples > 0:
                        self.ui.textLog.append(calc + " *" + str(mutliples + 1))
                    else:
                        self.ui.textLog.append(calc)

def main():
    """Launches Qt and creates an instance of ThinX."""
    app = QtWidgets.QApplication(sys.argv)
    window = ThinX()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
