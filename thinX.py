#!/usr/bin/env python

import sys
from PyQt4 import QtGui
from ui_thinX import Ui_MainWindow
import namespace
import xbrl


class thinX(QtGui.QMainWindow):
    """The main app class. Handles the GUI and various XBRL utilities."""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__init_statusbar()
        self.__init_connections()
        self.filename = ""
        self.unit_config_file = "units.ini"

    def __init_connections(self):
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionUnits.triggered.connect(self.units)
        self.ui.actionContexts.triggered.connect(self.contexts)
        self.ui.actionAbout.triggered.connect(self.about)

    def __init_statusbar(self):
        self.status = QtGui.QLabel()
        self.reset_status()
        self.statusBar().addPermanentWidget(self.status)

    def about(self):
        self.ui.textLog.clear()
        self.ui.textLog.append('<html><head/><body><p align=\"center\"><span '
                               'style=\"font-size:24pt; font-weight:600;\">'
                               'thinX</span></p></body></html>')

        self.ui.textLog.append('<html><head/><body><p align=\"center\">'
                               '<span style=\" font-size:10pt;\">thinX '
                               'is an open source XBRL toolkit developed '
                               'by<br>Austin M. Matherne and released '
                               'under the WTFPL.</span></p><p align='
                               '\"center\">https://github.com/AustinMatherne/'
                               'thinX</p></body></html>')

    def reset_status(self):
        """Resets the text in the status bar."""
        self.status.setText("Open an Instance Document to Begin ")

    def open(self):
        """Prompts the user to open an XBRL instance document and stores the
        file path in self.filename.

        """
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
                "You Must Open an Instance Document Before Processing ")
            return
        else:
            fixed = False
            logs = []
            tree = namespace.parse_xmlns(self.filename)
            root = tree.getroot()
            registries = xbrl.get_units(self.unit_config_file)
            for registry in registries:
                reg = registries[registry]
                prefix = "xmlns:" + reg["Prefix"]
                ns = reg["Namespace"]
                measures = reg["Measures"]
                log = xbrl.add_namespace(root, prefix, ns, measures)
                if log:
                    logs.append(log)
                    fixed = True
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            self.ui.textLog.clear()
            if fixed == True:
                self.status.setText("Unit Cleansing Complete ")
                for dict in logs:
                    for item in dict:
                        self.ui.textLog.append(item +" > " + dict[item])
            else:
                self.status.setText("No Units Found to Fix ")


    def contexts(self):
        """Removes unused contexts from self.filename."""
        if self.filename == "":
            self.status.setText(
                "You Must Open an Instance Document Before Processing ")
            return
        else:
            tree = namespace.parse_xmlns(self.filename)
            root = tree.getroot()
            log = xbrl.clean_contexts(root)
            namespace.fixup_xmlns(root)
            tree.write(self.filename, xml_declaration=True)
            self.ui.textLog.clear()
            if not log:
                self.status.setText("No Unused Contexts Found in File ")
            else:
                self.status.setText("Unused Contexts Removed ")
                for item in log:
                    self.ui.textLog.append(item)


def main():
    """Launches Qt and creates an instance of thinX."""
    app = QtGui.QApplication(sys.argv)
    window = thinX()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
