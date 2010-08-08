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

class Dialog():
    """Simple GUI to find out which server to add the torrent"""

    server = None
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect('destroy', lambda w: gtk.main_quit())
        combo_box = gtk.combo_box_entry_new_text()
        combo_box.child.connect('changed', self.changed)
        combo_box.child.connect('key_release_event', self.key_press)

        for server in servers:
            combo_box.append_text(server)
        combo_box.set_active(0)

        window.add(combo_box)
        window.show_all()

        window.show()
        #combo_box = gtk.combo_box_entry_new_text()

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
        tc.stop(id)
        # remote the .torrent file!
        if 'http://' not in tor:
            'deleting', tor
            os.remove(tor)

add_torrent(sys.argv[1:])
