#! /usr/bin/python3

import sys
import vlc

from PyQt5 import QtGui, QtCore, QtWidgets
from gui.spinner import QtWaitingSpinner


class Player(QtWidgets.QWidget):
    """A simple Media Player using VLC and Qt """
    def __init__(self, cameras = None, master=None):
        QtWidgets.QWidget.__init__(self, master)
        self.setWindowTitle("VTGS Multicamera View")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setGeometry(500, 200, 1280, 720)

        self.cameras = cameras
        print(self.cameras)

        # Create a basic VLC instance and an empty player
        # Setup a handler that switches the stack to the video output once the video itself actually starts playing
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.event_manager = self.media_player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerVout, self._show_video_)

        # Set the window background color
        self.background_color = QtGui.QColor(0, 0, 0)
        self.foreground_color = QtGui.QColor(255,255,255)
        palette =  QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, self.background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Setup trigger for the context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_)

        # Internal properties
        self.started = False

        # Initialize the window
        self._create_()
        self._start_()

    def _create_(self):
        ''' Setup the user interface '''

        ### Base Layout

        # Use a stacked layout so widgets can overlap
        # Add a resize widget which uses a vbox layout to push a grip to the bottom right.
        layout = QtWidgets.QStackedLayout()
        layout.setStackingMode(QtWidgets.QStackedLayout.StackOne)
        self.setLayout(layout)
        # Keep a reference to this one to switch between visible objects
        self.layout = layout

        ### Views

        # Loading view
        loading_widget = QtWidgets.QWidget(self)
        loading_layout = QtWidgets.QVBoxLayout()
        loading_label = QtWidgets.QLabel("Loading", loading_widget)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.WindowText, self.foreground_color)
        loading_label.setPalette(palette)
        loading_label.setFont(QtGui.QFont("Ubuntu", 28, QtGui.QFont.Medium))
        # Create the spinning animation and start it
        # TODO: Maybe replace with a gif animation rather than actually drawing it?
        loading_spinner = QtWaitingSpinner(loading_widget)
        loading_spinner.setColor(self.foreground_color)
        loading_spinner.setRevolutionsPerSecond(1.0)
        loading_spinner.start()
        # Set the layout spacing to give some room and align center
        loading_layout.setAlignment(QtCore.Qt.AlignHCenter)
        loading_layout.setSpacing(75)
        loading_layout.addWidget(loading_label)
        loading_layout.addWidget(loading_spinner)
        loading_widget.setLayout(loading_layout)
        self.layout.addWidget(loading_widget)
        self.loading_spinner = loading_spinner
        self.loading_widget = loading_widget

        # Stream view
        stream_widget = QtWidgets.QFrame()
        #stream_widget.setPalette(self.palette)
        #stream_widget.setAutoFillBackground(True)
        self.layout.addWidget(stream_widget)
        self.stream_widget = stream_widget

    def _context_(self, position):
        ''' Setup and show the context menu '''
        # Setup the menu so the action triggers the correct function
        # based on the current state of the streams.
        context = QtWidgets.QMenu()

        # Add menu items based on current state
        # Streaming start/pause
        tmp = "&Start"
        if self.started:
            tmp = "&Restart"
        context.addAction(tmp, self._start_)
        context.addSeparator()

        # Toggle fullscreen/views
        if self.isFullScreen():
            context.addAction("Leave &Fullscreen", self.showNormal)
        else:
            context.addAction("&Fullscreen", self.showFullScreen)
            resize = QtWidgets.QMenu("Resi&ze")
            resize.addAction("&Small", self.showSmall)
            resize.addAction("&Medium", self.showMedium)
            resize.addAction("&Large", self.showLarge)
            resize.addAction("&XLarge", self.showXLarge)
            context.addMenu(resize)
        context.addSeparator()

        self.cam_menu = QtWidgets.QMenu("&Cameras")
        for idx, item in enumerate(self.cameras):
            self.cam_menu.addAction("&{:d}. {:s}".format(idx+1, item['cam_name']), self.changeCamera, idx)
            self.cam_menu.exec
        context.addMenu(self.cam_menu)
        context.addSeparator()


        # Exit
        exit_action = context.addAction("E&xit", sys.exit)
        action = context.exec_(self.mapToGlobal(position))
    def changeCamera(self):
        action = self.sender()
        sender_text = action.text().strip('&')
        print(sender_text)
        cam_name = sender_text.split('.')[1].strip()
        print (cam_name)
        for idx, item in enumerate(self.cameras):
            if cam_name in item: print(idx)
        pass

    def _start_(self):
        ''' Open the overall VTGS video stream and start it '''
        print ("Starting stream")
        self.loading_spinner.start()
        self.layout.setCurrentWidget(self.loading_widget)

        # Load the media and set the vlc player
        self.media = self.instance.media_new('rtsp://public:cubesatell1te@198.82.154.114:9000/PSIA/streaming/channels/302')
        self.media_player.set_media(self.media)
        self.media.parse()

        # TODO: Set the stream title
        #self.setWindowTitle(self.media.get_meta(0))

        # The media player has to be 'connected' to the QFrame which is platform specific
        # (otherwise a video would be displayed in it's own window)
        # You have to give the ID of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform == "linux2" or sys.platform == "linux": # for Linux using the X Server
            self.media_player.set_xwindow(self.stream_widget.winId())
        elif sys.platform == "win32": # for Windows
            self.mediQtWidgetsaplayer.set_hwnd(self.stream_widget.winId())
        elif sys.platform == "darwin": # for MacOS
            self.media_player.set_agl(self.stream_widget.windId())

        # Start the stream
        self.media_player.play()
        self.started = True

    def _show_video_(self, event):
        ''' Show the video and not the waiting icon once it is actually playing '''
        print ("Showing video stream")
        self.loading_spinner.stop()
        self.layout.setCurrentWidget(self.stream_widget)

    def showSmall(self):
        self.resize(640, 360)

    def showMedium(self):
        self.resize(960, 540)

    def showLarge(self):
        self.resize(1280, 720)

    def showXLarge(self):
        self.resize(1600, 900)

    def mousePressEvent(self, event):
        self.old_position = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.old_position)
        #print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_position = event.globalPos()
