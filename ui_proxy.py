# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Documents and Settings\amather\My Documents\thinIceLabs\thinX\ui_proxy.ui'
#
# Created: Mon Feb  4 16:40:01 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_DialogProxy(object):
    def setupUi(self, DialogProxy):
        DialogProxy.setObjectName("DialogProxy")
        DialogProxy.setWindowModality(QtCore.Qt.WindowModal)
        DialogProxy.resize(205, 93)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogProxy.sizePolicy().hasHeightForWidth())
        DialogProxy.setSizePolicy(sizePolicy)
        DialogProxy.setMinimumSize(QtCore.QSize(205, 93))
        DialogProxy.setMaximumSize(QtCore.QSize(205, 93))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Glyphicons/icons/glyphicons_001_leaf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogProxy.setWindowIcon(icon)
        self.formLayout = QtGui.QFormLayout(DialogProxy)
        self.formLayout.setObjectName("formLayout")
        self.labelUsername = QtGui.QLabel(DialogProxy)
        self.labelUsername.setObjectName("labelUsername")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelUsername)
        self.lineUsername = QtGui.QLineEdit(DialogProxy)
        self.lineUsername.setObjectName("lineUsername")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineUsername)
        self.labelPassword = QtGui.QLabel(DialogProxy)
        self.labelPassword.setObjectName("labelPassword")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelPassword)
        self.linePassword = QtGui.QLineEdit(DialogProxy)
        self.linePassword.setObjectName("linePassword")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.linePassword)
        self.buttonBox = QtGui.QDialogButtonBox(DialogProxy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(DialogProxy)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DialogProxy.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DialogProxy.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogProxy)

    def retranslateUi(self, DialogProxy):
        DialogProxy.setWindowTitle(QtGui.QApplication.translate("DialogProxy", "Proxy Authorization", None, QtGui.QApplication.UnicodeUTF8))
        self.labelUsername.setText(QtGui.QApplication.translate("DialogProxy", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPassword.setText(QtGui.QApplication.translate("DialogProxy", "Password", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
