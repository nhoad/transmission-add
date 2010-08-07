#!/usr/bin/python
'''
File: main.py
Author: Nathan Hoad
Description: Adds torrents to transmission with nifty combo box
'''

from PyQt4 import QtGui, QtCore
import sys
import os
import transmissionrpc

# clients can be ip addresses or domain names
clients = ('desktop', 'media')

class Dialog(QtGui.QWidget):
    server_url = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Select A Transmission Host')
        self.button = QtGui.QPushButton('OK', self)

        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.addItems(clients)

        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.click)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.combo_box)
        vbox.addWidget(self.button)
        self.setLayout(vbox)
        self.resize(150, 20)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.click()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()
        
    def click(self):
        self.server_url = str(self.combo_box.currentText())
        self.close()

    def server(self):
        return self.server_url

def add_torrent(torrents):
    d = Dialog()
    d.show()
    app.exec_()

    server = d.server()
    print "connecting to", server

    if server is None:
        print "No server was specified!"
        sys.exit(1)

    tc = transmissionrpc.Client(server, port=9091)

    for tor in torrents:
        result = tc.add_url(tor)
        id = result.keys()[0]
        # pause the torrents right away!
        tc.stop(id)
        # remote the .torrent file!
        if "http://" not in tor:
            os.remove(tor)

app = QtGui.QApplication(sys.argv)
add_torrent(sys.argv[1:])
