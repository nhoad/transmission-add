#!/usr/bin/python
'''
File: main.py
Author: Nathan Hoad
Description: Adds torrents to transmission with nifty combo box
'''

import pygtk
pygtk.require('2.0')
import gtk

import sys
import os
import transmissionrpc

#servers can be ip addresses or domain names
servers = ('desktop', 'media')
delete = True
start = False


class Dialog():
    """Simple GUI to find out which server to add the torrent"""
    server = None

    def __init__(self):
        self.window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title('Select a server to add a client to')
        window.connect('destroy', lambda w: gtk.main_quit())
        combo_box = gtk.combo_box_entry_new_text()

        for server in servers:
            combo_box.append_text(server)

        delete_check = gtk.CheckButton("_Delete torrent file")
        pause_check = gtk.CheckButton("_Start when added")

        delete_check.set_active(delete)
        pause_check.set_active(start)

        delete_check.connect("toggled", self.toggled, "delete")
        pause_check.connect("toggled", self.toggled, "pause")

        delete_check.connect('key_release_event', self.key_press)
        pause_check.connect('key_release_event', self.key_press)

        add_button = gtk.Button(stock=gtk.STOCK_ADD)

        add_button.connect('clicked', self.clicked)

        combo_box.child.connect('changed', self.changed)
        combo_box.child.connect('key_release_event', self.key_press)
        combo_box.set_active(0)

        hbox = gtk.HBox(True, 2)
        hbox.add(delete_check)
        hbox.add(pause_check)

        hbox_top = gtk.HBox(True, 2)

        hbox_top.add(combo_box)
        hbox_top.add(add_button)

        vbox = gtk.VBox(True, 2)
        vbox.add(hbox_top)
        vbox.add(hbox)

        window.add(vbox)
        window.set_resizable(False)
        window.show_all()
        window.show()

    def toggled(self, widget, data=None):
        if data == "delete":
            delete = widget.get_active()
        if data == "pause":
            start = widget.get_active()

    def clicked(self, button):
        gtk.main_quit()

    def key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)

        if keyname in ("KP_Enter", "Return", "Enter"):
            gtk.main_quit()
        elif keyname == "Escape":
            gtk.main_quit()
            sys.exit(0)

    def changed(self, combo_box):
        self.server = combo_box.get_text()

        # in case it's just blank, make it None
        if not self.server:
            self.server = None


def add_torrent(torrents):
    d = Dialog()
    gtk.main()

    server = d.server
    print "connecting to", server

    if server is None:
        print "No server was specified!"
        sys.exit(1)

    tc = transmissionrpc.Client(server, port=9091)

    for tor in torrents:
        result = tc.add_url(tor)
        id = result.keys()[0]
        # pause the torrents right away!
        if not start:
            print "stopping", id
            tc.stop(id)

        # remote the .torrent file!
        if 'http://' not in tor and delete:
            print 'deleting', tor
            os.remove(tor)
    else:
        print "No torrents to add!"

add_torrent(sys.argv[1:])
