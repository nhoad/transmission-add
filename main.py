#!/usr/bin/python2
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
import time

import threading
gtk.gdk.threads_init()

#servers can be ip addresses or domain names
servers = ('desktop', '192.168.1.75')
delete = True
start = False


class AutoTimer(threading.Thread):
    """docstring for AutoTimer"""
    def __init__(self, dialog, time_to_wait):
        super(AutoTimer, self).__init__()
        print "Hello from AutoTimer!"
        self.dialog = dialog
        self.time_to_wait = time_to_wait

    def run(self):
        for i in range(self.time_to_wait, 0, -1):
            self.dialog.label.set_text("Auto-Adding in %d" % i)
            time.sleep(1)

        self.dialog.hide()

        print "Wahhh??"

class Dialog():
    """Simple GUI to find out which server to add the torrent"""
    server = None

    def __init__(self):
        self.window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title('Select a server to add %s to' % sys.argv[1])
        window.connect('destroy', lambda w: gtk.main_quit())
        combo_box = gtk.combo_box_entry_new_text()
        self.delete = delete
        self.start = start

        for server in servers:
            combo_box.append_text(server)

        delete_check = gtk.CheckButton("_Delete torrent file")
        pause_check = gtk.CheckButton("_Start when added")

        delete_check.set_active(delete)
        pause_check.set_active(start)

        delete_check.connect("toggled", self.toggled, "delete")
        pause_check.connect("toggled", self.toggled, "pause")

        delete_check.connect('key_release_event', self.toggled)
        pause_check.connect('key_release_event', self.toggled)

        add_button = gtk.Button(stock=gtk.STOCK_ADD)

        add_button.connect('clicked', self.clicked)

        combo_box.child.connect('changed', self.changed)
        combo_box.child.connect('key_release_event', self.key_press)
        combo_box.set_active(0)

        hbox = gtk.HBox(True, 2)
        hbox.add(delete_check)
        hbox.add(pause_check)

        self.label = gtk.Label("");
        hbox.add(self.label)

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

    def hide(self):
        gtk.main_quit()

    def toggled(self, widget, data=None):
        if data == "delete":
            self.delete = widget.get_active()
        if data == "pause":
            self.start = widget.get_active()

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
    t = AutoTimer(d, 5)
    # this drops threads when the user closes the program and such
    t.daemon = True
    t.start()
    gtk.main()

    server = d.server
    print "connecting to", server

    if server is None:
        print "No server was specified!"
        sys.exit(1)

    start = d.start
    delete = d.delete
    tc = transmissionrpc.Client(server, port=9091)

    for tor in torrents:
        print "adding", tor
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

add_torrent(sys.argv[1:])
