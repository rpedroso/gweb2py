#!/usr/bin/env python
# coding: utf-8
import __builtin__
import os
import sys
os.putenv('WINGDB_ACTIVE', '1')

try:
    import gobject
    gobject.threads_init()

    import vte
    import pygtk
    pygtk.require('2.0')
    import gtk
    __builtin__.USE_VTE = True
except ImportError:
    __builtin__.USE_VTE = False

import wx
import wx.lib.dialogs
import wx.lib.mixins.listctrl as listmix
import wx.lib.flatnotebook as fnb

import dircache
import re


__builtin__.opj = os.path.join
__builtin__.APP_PATH = os.path.realpath(os.path.dirname(__file__))
__builtin__.PORT = 8000
__builtin__.IS_MAC = 'wxMac' in wx.PlatformInfo
__builtin__.IS_WIN = 'wxMSW' in wx.PlatformInfo


def get_dir_file(filepath):
    filepath_list = filepath.split(os.sep)
    for d in ('controllers', 'views', 'models',
            'static', 'uploads', 'modules'):
        if d in filepath_list:
            idx = filepath_list.index(d) + 1
            if filepath_list[idx:]:
                return '[%s]%s' % (d[0].upper(), opj(*filepath_list[idx:]))
    return filepath_list[-1]

__builtin__.get_dir_file = get_dir_file

from customfont import load_font
load_font(opj('font', 'UbuntuMono-BI.ttf'))
load_font(opj('font', 'UbuntuMono-B.ttf'))
load_font(opj('font', 'UbuntuMono-RI.ttf'))
load_font(opj('font', 'UbuntuMono-R.ttf'))


def arguments():
    """docstring for arguments"""
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('path', type=str, help='web2py path', nargs='?')
    parser.add_argument('-p', type=int, dest='port', help="port to bind")
    if 'gtk2' in wx.PlatformInfo:
        parser.add_argument('--editor', type=str, dest='editor',
            help="editor to use (vim or stc)")
        args = parser.parse_args()
    else:
        args = parser.parse_args()
        args.editor = None

    return args


if __name__ == '__main__':
    args = arguments()

    if args.editor == 'stc':
        __builtin__.USE_VTE = False

    if args.port:
        __builtin__.PORT = int(args.port)

    app = wx.App(False)
    from main import Main
    Main(args.path)
    app.MainLoop()

    # wake up server to let him quit
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', __builtin__.PORT))
    except socket.error:
        pass
    finally:
        s.close()
