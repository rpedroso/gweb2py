#!/usr/bin/env python
# coding: utf-8

import os
import sys
import wx
import controls


class Frame(wx.Frame):

    def __init__(self, parent, size):
        wx.Frame.__init__(self, parent, size=size, title="gweb2py",
                style=(wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN))
        #self.SetDoubleBuffered(True)

        self.server = None
        self.panel = None

        #Build menus
        menuBar = wx.MenuBar()

        menu = wx.Menu()
        self.menu_item_w2p_open = menu.Append(wx.ID_ANY, "&Open",
                "Open a web2py folder and start webserver")
        self.menu_item_w2p_close = menu.Append(wx.ID_ANY, "&Close",
                "Close all files and stop webserver")
        menu.AppendSeparator()
        self.menu_item_w2p_reload = menu.Append(wx.ID_ANY, "&Reload",
                "Reload web server")
        menu.AppendSeparator()
        self.menu_item_w2p_quit = menu.Append(wx.ID_ANY, "&Quit",
                "Quit everything")
        menuBar.Append(menu, "&Web2py")
        self.menu_w2p = menu

        self.Bind(wx.EVT_MENU, self.OnMenuW2pOpen, self.menu_item_w2p_open)
        self.Bind(wx.EVT_MENU, self.OnMenuW2pClose, self.menu_item_w2p_close)
        self.Bind(wx.EVT_MENU, self.OnMenuW2pReload, self.menu_item_w2p_reload)
        self.Bind(wx.EVT_MENU, self.OnMenuW2pQuit, self.menu_item_w2p_quit)

        menu = wx.Menu()
        self.menu_item_app_new = menu.Append(wx.ID_ANY, "&New",
                "Create a new application")
        menuBar.Append(menu, "&Application")
        self.menu_app = menu

        self.Bind(wx.EVT_MENU, self.OnMenuAppNew, self.menu_item_app_new)

        menu = wx.Menu()
        self.menu_item_file_new = menu.Append(wx.ID_ANY,
                "&New\tCtrl-N", "Create a new file")
        self.menu_item_file_open = menu.Append(wx.ID_ANY,
                "&Open\tCtrl-O", "Open a file")
        self.menu_item_file_save = menu.Append(wx.ID_ANY,
                "&Save\tCtrl-S", "Save current file")
        #item4 = menu.Append(wx.ID_ANY, "&Close", "")
        menuBar.Append(menu, "&File")
        self.menu_file = menu

        self.Bind(wx.EVT_MENU, self.OnMenuFileNew, self.menu_item_file_new)
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, self.menu_item_file_open)
        self.Bind(wx.EVT_MENU, self.OnMenuFileSave, self.menu_item_file_save)
        #self.Bind(wx.EVT_MENU, self.OnMenuFileClose, item4)

        menu = wx.Menu()
        item1 = menu.Append(wx.ID_ANY, "Focus file &browser\tCtrl+1",
                "Set focus to file browser window")
        item2 = menu.Append(wx.ID_ANY, "Focus &editor\tCtrl+2",
                "Set focus to current editor window")
        menu.AppendSeparator()
        item3 = menu.Append(wx.ID_ANY, "&Previous tab\tCtrl+PageUp",
                "Previous tab")
        item4 = menu.Append(wx.ID_ANY, "&Next tab\tCtrl+PageDown",
                "Next tab")
        item5 = menu.Append(wx.ID_ANY, "&Close tab\tCtrl+w",
                "Close current tab.")
        menu.AppendSeparator()
        item6 = menu.Append(wx.ID_ANY, "&Clear current output window\tCtrl+K",
                "Clear contents of current output window")
        menuBar.Append(menu, "&Windows")
        self.menu_windows = menu

        self.Bind(wx.EVT_MENU, self.OnMenuFocusFileBrowser, item1)
        self.Bind(wx.EVT_MENU, self.OnMenuFocusNotebook, item2)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowsPrev, item3)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowsNext, item4)
        self.Bind(wx.EVT_MENU, self.OnMenuCloseTab, item5)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowClear, item6)

        self.menu_debug = wx.Menu()
        if IS_MAC:
            self.f2 = self.menu_debug.Append(wx.ID_ANY,
                    "&Enable/Disable debug\tCtrl+F2",
                    "Turn debugger on or off")
            self.f3 = self.menu_debug.Append(wx.ID_ANY,
                    "&Add/Remove breakpoint...\tCtrl+F3",
                    "Add or remove breakpoint...")
            self.f4 = self.menu_debug.Append(wx.ID_ANY,
                    "&Enable/Disable gluon debug \tCtrl+F4",
                    "Allow debugging web2py gluon code")
            self.menu_debug.AppendSeparator()
            self.f6 = self.menu_debug.Append(wx.ID_ANY,
                    "&Continue\tCtrl+F6",
                    "Continue to next breakpoint or until the end")
            self.f7 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug step\tCtrl+F7",
                    "Stop after one line of code.")
            self.f8 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug next\tCtrl+F8",
                    "Stop on the next line in or below the given frame.")
            self.f9 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug until\tCtrl+F9",
                    ("Stop when the line with the line number greater than "
                    "the current one is reached or when returning from "
                    "current frame"))
        else:
            self.f2 = self.menu_debug.Append(wx.ID_ANY,
                    "&Enable/Disable debug\tF2",
                    "Turn debugger on or off")
            self.f3 = self.menu_debug.Append(wx.ID_ANY,
                    "&Add/Remove breakpoint...\tF3",
                    "Add or remove breakpoint...")
            self.f4 = self.menu_debug.Append(wx.ID_ANY,
                    "&Enable/Disable gluon debug \tF4",
                    "Allow debugging web2py gluon code")
            self.menu_debug.AppendSeparator()
            self.f6 = self.menu_debug.Append(wx.ID_ANY,
                    "&Continue\tF6",
                    "Continue to next breakpoint or until the end")
            self.f7 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug step\tF7", "Stop after one line of code.")
            self.f8 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug next\tF8",
                    "Stop on the next line in or below the given frame.")
            self.f9 = self.menu_debug.Append(wx.ID_ANY,
                    "&Debug until\tF9",
                    ("Stop when the line with the line number greater than "
                    "the current one is reached or when returning from "
                    "current frame"))
        #item6 = self.menu_debug.Append(wx.ID_ANY, "&Eval \tF9", "")
        menuBar.Append(self.menu_debug, "&Debug")

        self.SetMenuBar(menuBar)

        # Status bar
        self.sb = wx.StatusBar(self)
        self.SetStatusBar(self.sb)

        # Timer
        self.timer = wx.Timer(self)

        # Bind menus events
        self.Bind(wx.EVT_MENU, self.OnMenuDebugUntil, self.f9)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugToggle, self.f2)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugContinue, self.f6)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugStep, self.f7)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugNext, self.f8)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugAllowGluon, self.f4)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugAddBP, self.f3)

        # Bind breakpoint event to remove breakpoints on double click
        self.Bind(controls.EVT_BPLIST_REMOVE, self.OnBPRemove)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_IDLE, self.OnTimer)

        self.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

        #self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

        #self.Show()

    def SendSizeEvent(self):
        if IS_MAC:
            w, h = self.GetSize()
            self.SetSize((w-1, h-1))
            self.SetSize((w, h))
        else:
            wx.Frame.SendSizeEvent(self)


def error(parent, msg):
    wx.MessageDialog(parent, msg, "Error",
            wx.OK | wx.ICON_ERROR).ShowModal()


def dialog_create_new_file(parent, default_dir=None):
    path = None
    dlg = wx.FileDialog(parent, "Create a new file",
                        defaultDir=default_dir,
                        style=wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE,
                        )

    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()

    dlg.Destroy()
    return path


def dialog_open_file(parent, default_dir=None):
    path = None
    dlg = wx.FileDialog(parent, "Open a file",
                        defaultDir=default_dir,
                        style=wx.FD_OPEN,
                        )

    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()

    dlg.Destroy()
    return path


def dialog_choose_web2py(parent):
    dirpath = None
    dlg = wx.DirDialog(parent, "Choose a directory",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           | wx.DD_CHANGE_DIR)

    if dlg.ShowModal() == wx.ID_OK:
        dirpath = dlg.GetPath()

    dlg.Destroy()
    return dirpath


def dialog_admin_password(parent):
    p = None
    dlg = wx.TextEntryDialog(parent, 'Admin Password', 'Admin Password', '')
    if dlg.ShowModal() == wx.ID_OK:
        p = dlg.GetValue().strip()
    dlg.Destroy()
    return p


#class IsIntValidator(wx.PyValidator):
#    def __init__(self):
#        wx.PyValidator.__init__(self)
#
#    def Clone(self):
#        return IsIntValidator(self.flag)
#
#    def Validate(self, win):
#        tc = self.GetWindow()
#        print tc, win
#        val = tc.GetValue()
#        return val.isdigit()


def dialog_debug_lineno(parent):
    dlg = wx.TextEntryDialog(parent, 'Line number', 'Line Number', '')
    while True:
        lineno = '0'
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            lineno = dlg.GetValue()
        if lineno.isdigit():
            break
    dlg.Destroy()
    return int(lineno)


def dialog_app_new(parent):
    p = None
    dlg = wx.TextEntryDialog(parent, 'App name', 'App name', '')
    if dlg.ShowModal() == wx.ID_OK:
        p = dlg.GetValue().strip()
    dlg.Destroy()
    return p
