#! /usr/bin/python

from __future__ import print_function

import gtk
gtk.gdk.threads_init()
import glib

import sys
import vlc
import time

from gettext import gettext as _

# Create a single vlc.Instance() to be shared by (possible) multiple players.

print ("Starting multiview interface")
#instance = vlc.Instance("--no-xlib", "--no-audio")
instance = vlc.Instance("--no-audio")

# Media URLs
urls = ['rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/301',
        'rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/201',
        'rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/101',
        'rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/302',
        'rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/202',
        'rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/102']


class VLCWidget(gtk.DrawingArea):
    """Simple VLC widget.

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """
    def __init__(self, *p):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        def handle_embed(*args):
            if sys.platform == 'win32':
                self.player.set_hwnd(self.window.handle)
            else:
                self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(320, 200)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))


class DecoratedVLCWidget(gtk.VBox):
    """Decorated VLC widget.

    VLC widget decorated with a player control toolbar.

    Its player can be controlled through the 'player' attribute, which
    is a Player instance.
    """
    def __init__(self, *p):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(*p)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)
        #self._toolbar = self.get_player_control_toolbar()
        #self.pack_start(self._toolbar, expand=False)

    def start(self):
        self.player.play()


class MultiVideoPlayer:
    """
    Camera multivew player.
    It plays multiple videos in a | 1 | 3 | split view.
    The three video feeds are rotated to the large view after several seconds.
    """
    def main(self):
        # Build main window and table for doing a 9x9 layout
        # Create 4 sub-views. Large view on the left and 3 small views on the right
        window=gtk.Window()
        table = gtk.Table(9, 9, True)
        window.add(table)
        large = gtk.HBox()
        small_top = gtk.HBox()
        small_center = gtk.HBox()
        small_bottom = gtk.HBox()

        # Setup the multiview layout
        table.attach(large, 0, 6, 0, 9)
        table.attach(small_top, 6, 9, 0, 3)
        table.attach(small_center, 6, 9, 3, 6)
        table.attach(small_bottom, 6, 9, 6, 9)

        # Create VLC widgets for the smaller views
        # Overview
        video_overview = DecoratedVLCWidget()
        video_overview.player.set_media(instance.media_new(urls[3]))
        video_overview.start()
        small_top.add(video_overview)

        video_3mdish = DecoratedVLCWidget()
        video_3mdish.player.set_media(instance.media_new(urls[4]))
        video_3mdish.start()
        small_center.add(video_3mdish)

        # VHF UHF
        video_vhf_uhf = DecoratedVLCWidget()
        video_vhf_uhf.player.set_media(instance.media_new(urls[5]))
        video_vhf_uhf.start()
        small_bottom.add(video_vhf_uhf)

        rotate_url = 0
        video_large = DecoratedVLCWidget()
        video_large.player.set_media(instance.media_new(urls[0]))
        video_large.start()
        large.add(video_large)

        window.fullscreen()
        window.set_default_size(800, 600)
        window.show_all()
        window.connect("destroy", gtk.main_quit)
        gtk.main()

if __name__ == '__main__':
    player = MultiVideoPlayer()
    player.main()
