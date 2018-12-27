#!/usr/bin/env python

# encoding: utf-8

# @author: Durand Wang

# @file: DarkRiverClient.py

# @time: 2018/12/7 17:41

from PyQt5 import QtGui, QtWidgets
from untitled import Ui_Dialog
import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

HOST = "127.0.0.1"
PORT = 5003
BUFSIZE = 1024
ADDR = (HOST, PORT)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)


class DarkRiverClient(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentMembersChanged = False      # refer if the current member has changed
        self.currentMembers = []                # every client store the current member locally
        self.ui = Ui_Dialog()                   # the user interface
        self.ui.setupUi(self)
        self.ui.sendBtnObj.clicked.connect(self.send)               # signal&slot send message button
        self.ui.cancelBtnObj.clicked.connect(self.cancel)           # signal&slot cancel message button
        self.ui.exitBtnObj.clicked.connect(self.exit)               # signal&slot
        # signal&slot if message browser changed, call self.membersBrowser
        self.ui.textBrowser.textChanged.connect(self.membersBrowser)    # if the textBrowser change, call the func
        self.setWindowTitle('Dark River v1.0')          # the subthread can append QWight content, but delete or change
        self.setWindowIcon(QtGui.QIcon('img/icon.ico'))  # will call error, so those move should in main thread
        self.show()                                      # use pyqt signal to do that
        # The main thread control ui, self.receive_thread control socket communication
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

    def send(self):
        """Messages sending"""
        msg = self.ui.textEdit.toPlainText()        # get the input
        if not msg:                                 # empty message
            return
        msg = msg.rstrip()                          # redundant spaces
        self.ui.textEdit.setText('')                # clean the input area
        sock.send(bytes(msg, 'utf8'))               # send message through socket
        if msg == '#exit':                          # quit chat room
            sock.close()
            Qapp = QtWidgets.QApplication.instance()
            Qapp.quit()

    def cancel(self):
        """Clean the message has typed in the box"""
        self.ui.textEdit.setText('')

    def membersBrowser(self):
        """Control the current member browser"""
        if not self.currentMembersChanged:          # do nothing if hasn't changed
            return
        self.ui.textBrowser_2.setPlainText('')      # clear the browser
        for member in self.currentMembers:          # display new data
            self.ui.textBrowser_2.append(member)

    def receive(self):
        """Messages receiving"""
        while True:
            try:
                msg = sock.recv(BUFSIZE).decode("utf8")
                if msg[0:2] == '$%':                # the current members information start with '$%'
                    self.currentMembersChanged = True
                    self.currentMembers.clear()
                    self.currentMembers = msg[2:].split('\t')
                else:
                    self.ui.textBrowser.append(msg)
                    self.ui.textBrowser.moveCursor(QtGui.QTextCursor.End)
            except OSError:                         # Connection has been cut
                break

    def exit(self):
        """exit the chat room"""
        self.ui.textEdit.setText('#exit')
        self.send()


app = QtWidgets.QApplication(sys.argv)
obj = DarkRiverClient()
sys.exit(app.exec_())
