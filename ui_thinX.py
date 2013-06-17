# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\amather\thinIceLabs\thinX\ui_thinX.ui'
#
# Created: Sun Jun 16 19:46:44 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(600, 350)
        MainWindow.setMinimumSize(QtCore.QSize(600, 350))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_001_leaf.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.textLog = QtGui.QTextEdit(self.centralwidget)
        self.textLog.setEnabled(True)
        self.textLog.setAutoFillBackground(False)
        self.textLog.setReadOnly(True)
        self.textLog.setObjectName(_fromUtf8("textLog"))
        self.horizontalLayout.addWidget(self.textLog)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuUtilities = QtGui.QMenu(self.menubar)
        self.menuUtilities.setObjectName(_fromUtf8("menuUtilities"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_144_folder_open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionExit = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_063_power.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon2)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionUnits = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_023_magnet.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUnits.setIcon(icon3)
        self.actionUnits.setObjectName(_fromUtf8("actionUnits"))
        self.actionContexts = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_413_posterous_spaces.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionContexts.setIcon(icon4)
        self.actionContexts.setObjectName(_fromUtf8("actionContexts"))
        self.actionAbout = QtGui.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_064_lightbulb.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon5)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionCalculations = QtGui.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_041_charts.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCalculations.setIcon(icon6)
        self.actionCalculations.setObjectName(_fromUtf8("actionCalculations"))
        self.actionLabels = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/Glyphicons/icons/glyphicons_100_font.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLabels.setIcon(icon7)
        self.actionLabels.setObjectName(_fromUtf8("actionLabels"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuUtilities.addAction(self.actionContexts)
        self.menuUtilities.addAction(self.actionUnits)
        self.menuUtilities.addAction(self.actionLabels)
        self.menuUtilities.addAction(self.actionCalculations)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuUtilities.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionContexts)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionUnits)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionLabels)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCalculations)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "thinX", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuUtilities.setTitle(_translate("MainWindow", "Utilities", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionOpen.setToolTip(_translate("MainWindow", "Open Instance Document", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionUnits.setText(_translate("MainWindow", "Comply with UTR", None))
        self.actionContexts.setText(_translate("MainWindow", "Remove Unused Contexts", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionCalculations.setText(_translate("MainWindow", "Find Duplicate Calculations", None))
        self.actionLabels.setText(_translate("MainWindow", "Remove Unused Labels", None))
        self.actionLabels.setToolTip(_translate("MainWindow", "Remove Unused Labels", None))

import icons_rc
