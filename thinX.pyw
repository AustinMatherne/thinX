#!/usr/bin/env python

import namespace
import sys
import re
from PyQt4 import QtGui
from ui_thinX import Ui_MainWindow
import xbrl


class ThinX(QtGui.QMainWindow):
    """The main app class. Handles the GUI and various XBRL utilities."""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
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

    def __init_statusbar(self):
        self.status = QtGui.QLabel()
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
            + self.get_version() + "</p></body></html>"
        )

    def reset_status(self):
        """Resets the text in the status bar."""
        self.status.setText("Open an Instance Document to Begin ")

    def open_fail(self, file_name):
        """Logs a file that failed to open to the status bar."""
        self.status.setText("Failed to Open: " + file_name + " ")

    def open(self):
        """Prompts the user to open an XBRL instance document and stores the
        file path in self.filename.

        """
        self.ui.textLog.clear()
        self.filename = QtGui.QFileDialog.getOpenFileName(
            filter="Instance Document (*.XML *.XBRL)")
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
            registries = xbrl.get_units(self.unit_config_file)
            prefixes = []
            for registry in registries:
                reg = registries[registry]
                prefix = "xmlns:" + reg["Prefix"]
                prefixes.append(prefix)
                ns = reg["Namespace"]
                measures = reg["Measures"]
                log = xbrl.add_namespace(root, prefix, ns, measures)
                if log:
                    logs.append(log)
                    fixed = True
            check = xbrl.extended_measures(root, prefixes,
                                           self.unit_config_file)
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            self.ui.textLog.clear()
            if fixed == True:
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
                tree = namespace.parse_xmlns(calc_linkbase)
            except:
                self.ui.textLog.clear()
                self.open_fail(calc_linkbase)
                return

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
                for item in log:
                    if log[item] > 0:
                        self.ui.textLog.append(item + " *" + str(log[item] + 1))
                    else:
                        self.ui.textLog.append(item)


def main():
    """Launches Qt and creates an instance of ThinX."""
    app = QtGui.QApplication(sys.argv)
    window = ThinX()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
