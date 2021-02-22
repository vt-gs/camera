#! /usr/bin/python3

import sys
import os
import argparse
import json
import subprocess
from PyQt5 import QtGui, QtCore, QtWidgets
from gui.player import Player
#from gui.spinner import *

if __name__ == "__main__":
    """ Main entry point to start the service. """
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="VTGS Camera Client",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--cam_path',
                       dest='cam_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'config']),
                       help="Camera Configuration File Path",
                       action="store")
    cfg.add_argument('--cam_file',
                       dest='cam_file',
                       type=str,
                       default="cameras.json",
                       help="Camera Configuration File",
                       action="store")
    args = parser.parse_args()
#--------END Command Line argument parser------------------------------------------------------

    subprocess.run(["reset"])
    #print(sys.path)
    fp_cfg = '/'.join([args.cam_path,args.cam_file])
    print (fp_cfg)
    if not os.path.isfile(fp_cfg) == True:
        print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_cfg))
    with open(fp_cfg, 'r') as json_data:
        cam = json.load(json_data)
        json_data.close()
    # print(cam)
    # for idx,item in enumerate(cam):
    #     print(idx+1, item['cam_name'])
    #     print(item['hires_url'])
    #     print(item['hires_url'])
    #     print()
    # sys.exit()


    # Initialize the Qt Application and the main window
    app = QtWidgets.QApplication(sys.argv)
    player = Player(cameras=cam)
    player.setWindowFlags(QtCore.Qt.MaximizeUsingFullscreenGeometryHint |
                          QtCore.Qt.FramelessWindowHint)
    player.show()
    sys.exit(app.exec_())
