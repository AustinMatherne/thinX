#!/usr/bin/env python

import esky
import os
from PySide import QtGui
import sys
from ui_proxy import Ui_DialogProxy
import urllib.request


class ProxyPopup(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_DialogProxy()
        self.ui.setupUi(self)
        self.ui.linePassword.setEchoMode(QtGui.QLineEdit.EchoMode.Password)

def check(self):
    proxy_url = auth_prompt(self)
    proxy = urllib.request.ProxyHandler({"http": proxy_url})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    try:
        if(self.app.find_update() != None):
            self.app.auto_update()
            appexe = esky.util.appexe_from_executable(sys.executable)
            os.execv(appexe,[appexe] + sys.argv[1:])
        else:
            return True
    except Exception:
        return False

def auth_prompt(self):
    self.dialog = ProxyPopup()
    self.dialog.exec_()
    http_proxy_user = self.dialog.ui.lineUsername.text()
    http_proxy_passwd = self.dialog.ui.linePassword.text()
    http_proxy_server = "inetproxy.stp.mrll.com"
    http_proxy_port = "80"

    proxy_url = "http://%s:%s@%s:%s" % (http_proxy_user, http_proxy_passwd,
                                        http_proxy_server, http_proxy_port)

    return proxy_url