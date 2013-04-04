# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Documents and Settings\amather\My Documents\thinIceLabs\thinX\ui_thinX.ui'
#
# Created: Mon Feb  4 16:40:00 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 350)
        MainWindow.setMinimumSize(QtCore.QSize(600, 350))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_001_leaf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textLog = QtGui.QTextEdit(self.centralwidget)
        self.textLog.setEnabled(True)
        self.textLog.setAutoFillBackground(False)
        self.textLog.setReadOnly(True)
        self.textLog.setObjectName("textLog")
        self.horizontalLayout.addWidget(self.textLog)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuUtilities = QtGui.QMenu(self.menubar)
        self.menuUtilities.setObjectName("menuUtilities")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_144_folder_open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_063_power.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon2)
        self.actionExit.setObjectName("actionExit")
        self.actionUnits = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_023_magnet.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUnits.setIcon(icon3)
        self.actionUnits.setObjectName("actionUnits")
        self.actionContexts = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_413_posterous_spaces.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionContexts.setIcon(icon4)
        self.actionContexts.setObjectName("actionContexts")
        self.actionAbout = QtGui.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_064_lightbulb.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon5)
        self.actionAbout.setObjectName("actionAbout")
        self.actionCalculations = QtGui.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_041_charts.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCalculations.setIcon(icon6)
        self.actionCalculations.setObjectName("actionCalculations")
        self.actionUpdate = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_057_history.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUpdate.setIcon(icon7)
        self.actionUpdate.setObjectName("actionUpdate")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuUtilities.addAction(self.actionContexts)
        self.menuUtilities.addAction(self.actionUnits)
        self.menuUtilities.addAction(self.actionCalculations)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionUpdate)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuUtilities.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionContexts)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionUnits)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCalculations)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "thinX", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuUtilities.setTitle(QtGui.QApplication.translate("MainWindow", "Utilities", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setToolTip(QtGui.QApplication.translate("MainWindow", "Open Instance Document", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUnits.setText(QtGui.QApplication.translate("MainWindow", "Comply with UTR", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContexts.setText(QtGui.QApplication.translate("MainWindow", "Remove Unused Contexts", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCalculations.setText(QtGui.QApplication.translate("MainWindow", "Find Duplicate Calculations", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUpdate.setText(QtGui.QApplication.translate("MainWindow", "Check for Updates", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
