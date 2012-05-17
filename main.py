#!/usr/bin/env python
# coding: utf-8
import __builtin__
import os
import sys
os.putenv('WINGDB_ACTIVE', '1')

import wx
import toplevel
import panels
import controls


class Web2pyServer(object):

    def __init__(self, parent, app_path, w2p_path):
        self.parent = parent
        self.app_path = app_path
        self.w2p_path = w2p_path
        self.is_running = False
        self.pid = 0
        self.process = None

    def stop(self):
        if self.pid:
            stream = self.process.GetOutputStream()
            stream.write('__quit__\n')
            stream.flush()
            #wx.CallAfter(self.process.Kill, self.pid, wx.SIGTERM)

        self.is_running = False

    def start(self, passwd, port):
        self.process = wx.Process(self.parent)
        self.process.Redirect()
        p = self.app_path
        sys.path.insert(0, self.w2p_path)

        os.chdir(self.w2p_path)

        if not os.path.isfile('web2py.py'):
            self.process = None
            raise Exception('%s: Execution failed' % 'web2py.py')

        if passwd:
            passwd = passwd.strip()
            from gluon.main import save_password
            save_password(passwd, port)

        cmd = '"%s" -u "%s" %s "%s"' % (sys.executable,
                opj(p, 'gw2pserver.py'), port, self.w2p_path)

        self.pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)

        if self.pid == 0:
            self.process = None
            raise Exception('%s: Execution failed' % 'web2py.py')
        self.is_running = True


class Main(toplevel.Frame):

    def __init__(self, w2p_path):
        # Bind menus events
        toplevel.Frame.__init__(self, None, size=(800, 600))
        self.Bind(controls.EVT_SHELL, self.on_shell)

        self.Show()

        if w2p_path:
            self.open_web2py(w2p_path)

    def toggle_menu_w2p(self):
        self.menu_w2p.Enable(self.menu_item_w2p_open.GetId(),
                not bool(self.panel))
        self.menu_w2p.Enable(self.menu_item_w2p_close.GetId(),
                bool(self.panel))

    def toogle_menu_app(self):
        item = 'menu_item_app_new'
        self.menu_app.Enable(getattr(self, item).GetId(), bool(self.panel))

    def toggle_menu_file(self):
        if self.panel:
            flag = self.panel.notebook_is_editor()
            flag2 = True
        else:
            flag = False
            flag2 = False

        self.menu_file.Enable(self.menu_item_file_save.GetId(), flag)
        self.menu_file.Enable(self.menu_item_file_new.GetId(), flag2)

    def toggle_menu_windows(self):
        for item in self.menu_windows.GetMenuItems():
            self.menu_windows.Enable(item.GetId(), bool(self.panel))

    def toggle_menu_debug(self):
        #print 'aqui'
        self.menu_debug.Enable(self.f2.GetId(), True)
        items = ['f3', 'f4', 'f6', 'f7', 'f8', 'f9']
        if self.panel and self.panel.is_debug_on():
            for item in items:
                self.menu_debug.Enable(getattr(self, item).GetId(), True)
        else:
            if not self.panel:
                items.append('f2')
            for item in items:
                self.menu_debug.Enable(getattr(self, item).GetId(), False)

    def OnProcessEnded(self, evt):
        if self.panel:
            self.OnTimer(None)
            self.panel.log_append_text('stdout', "webserver stopped")
        self.server.process.Destroy()
        self.server.process = None
        self.server = None

    def OnClose(self, evt):
        if self.panel:
            self.timer.Stop()
            self.panel.ClosePanel(self.DoClose)
        else:
            evt.Skip()

    def DoClose(self, can_close):
        if can_close:
            if self.server and self.server.process:
                self.server.stop()
            self.Destroy()

    def open_web2py(self, w2p_path=None):
        if not w2p_path:
            w2p_path = toplevel.dialog_choose_web2py(self)
            if not w2p_path:
                return

        w2p_path = os.path.normpath(w2p_path)
        self.server = Web2pyServer(self, APP_PATH, w2p_path)
        p = toplevel.dialog_admin_password(self)
        try:
            self.server.start(p, PORT)
        except Exception, e:
            import traceback
            err = traceback.format_exc()
            toplevel.error(self,
                    'Failed to start webserver\n\n'
                    'reason:\n%s\n\n'
                    'traceback:\n'
                    '%s' % (err.splitlines()[-1], err))
            return

        os.chdir(w2p_path)
        self.panel = panels.MainPanel(self, w2p_path)
        self.SendSizeEvent()
        self.timer.Start(500)

    def OnMenuAppNew(self, evt):
        name = toplevel.dialog_app_new(self)
        if name:
            try:
                self.panel.app_new(name)
            except IOError, e:
                toplevel.error(self,
                        'Could not create application %s\n\n'
                        'Possible causes:\n'
                        "- You do not have a 'welcome.w2p' file in %s\n"
                        "- There is already an application named %s" % (
                            name, os.path.dirname(e.filename), name))

    def OnMenuW2pOpen(self, evt):
        if not self.panel:
            self.open_web2py()
        else:
            self.panel.ClosePanel(self.ClosedPanel)
            self.open_web2py()

    def ClosedPanel(self, can_close):
        if can_close:
            if self.server and self.server.process:
                self.server.stop()
            #self.w2p_path = None
            self.panel.Destroy()
            self.panel = None

    def OnMenuW2pClose(self, evt):
        if self.panel:
            self.panel.ClosePanel(self.ClosedPanel)

    def OnMenuW2pQuit(self, evt):
        if self.panel:
            self.panel.ClosePanel(self.DoClose)
        else:
            self.Close()

    def OnMenuFileNew(self, evt):
        path = self.panel.tree_get_selected_item_data()
        if path and not os.path.isdir(path):
            path = os.path.dirname(path)

        filepath = toplevel.dialog_create_new_file(self, default_dir=path)
        if filepath:
            open(filepath, 'w').close()
            self.panel.notebook_new_file(filepath)

    def OnMenuFileOpen(self, evt):
        path = self.panel.tree_get_selected_item_data()
        if path and not os.path.isdir(path):
            path = os.path.dirname(path)

        filepath = toplevel.dialog_open_file(self, default_dir=path)
        if filepath:
            self.panel.notebook_open_file(filepath)

    def OnMenuFileSave(self, evt):
        self.panel.notebook_save_file()

    def OnMenuFocusFileBrowser(self, evt):
        self.panel.tree_setfocus()

    def OnMenuFocusNotebook(self, evt):
        self.panel.notebook_setfocus()

    def OnMenuWindowsPrev(self, evt):
        self.panel.notebook_advance(False)

    def OnMenuWindowsNext(self, evt):
        self.panel.notebook_advance(True)

    def OnMenuCloseTab(self, evt):
        self.panel.notebook_close_current_tab()

    def OnMenuWindowClear(self, evt):
        self.panel.log_clear_current()

    def OnMenuDebugNext(self, evt):
        if self.server and self.server.process is not None:
            self.sb.SetStatusText("running")
            stream = self.server.process.GetOutputStream()
            stream.write('set_next\n')

    def OnMenuDebugStep(self, evt):
        if self.server and self.server.process is not None:
            self.sb.SetStatusText("running")
            stream = self.server.process.GetOutputStream()
            stream.write('set_step\n')

    def OnMenuDebugContinue(self, evt):
        if self.server and self.server.process is not None:
            self.sb.SetStatusText("running")
            stream = self.server.process.GetOutputStream()
            stream.write('set_continue\n')

    def OnMenuDebugToggle(self, evt):
        if self.server and self.server.process is not None:
            self.sb.SetStatusText("")
            self.panel.app_debug_mode(True)
            stream = self.server.process.GetOutputStream()
            stream.write('toggle_debug\n')

    def OnMenuDebugAllowGluon(self, evt):
        if self.server and self.server.process is not None:
            stream = self.server.process.GetOutputStream()
            stream.write('toggle_gluon\n')

    def OnMenuDebugUntil(self, evt):
        if self.server and self.server.process is not None:
            self.sb.SetStatusText("running")
            stream = self.server.process.GetOutputStream()
            stream.write('set_until\n')

    def OnMenuDebugAddBP(self, evt):
        lineno = toplevel.dialog_debug_lineno(self)
        if lineno:
            filename = self.panel.set_break(lineno)
            if filename:
                stream = self.server.process.GetOutputStream()
                stream.write('set_break %s %d\n' % (filename, lineno))

    def OnBPRemove(self, evt):
        lineno, filename = evt.GetMyVal()
        stream = self.server.process.GetOutputStream()
        stream.write('clear_break %s %s\n' % (filename, lineno))

        self.panel.clear_break(lineno, filename)

    def on_shell(self, event):
        text = event.text
        if self.server and self.server.process is not None:
            stream = self.server.process.GetOutputStream()
            stream.write('SH:%s\n' % text)

    def from_debugger(self, text):
        command, text = text.split(':', 1)
        if command == 'STEP':
            self.trace_line(text.strip())
        elif command == 'RES':
            lenght, text = text.split(':', 1)
            self.show_eval(text, lenght)
        elif command == "STOP":
            self.stop_debug()
        elif command == "START":
            self.sb.SetStatusText("serving")

    def show_eval(self, text, lenght):
        missing = int(lenght) - len(text)
        if missing > 0:
            if self.server and self.server.process is not None:
                stream = self.server.process.GetInputStream()
                text += stream.read(missing)
        self.panel.log_append_text('shell', text)

    def OnTimer(self, evt=None):
        self.toggle_menu_w2p()
        self.toogle_menu_app()
        self.toggle_menu_file()
        self.toggle_menu_windows()
        self.toggle_menu_debug()
        if not self.panel:
            return

        if self.server and self.server.process is not None:
            if self.server.process.IsErrorAvailable():
                stream = self.server.process.GetErrorStream()
                text = ''
                while True:
                    t = stream.readline()
                    if not t:
                        break
                    text += t
                sys.stderr.write(text)
                if self.panel:
                    self.panel.log_append_text('stderr', text)
                return

            stream = self.server.process.GetInputStream()
            if stream and stream.CanRead():
                while True:
                    text = stream.readline()
                    if not text.strip():
                        break
                    try:
                        func, text = text.split(':', 1)
                    except ValueError, e:
                        self.panel.log_append_text('stdout', text)
                        return
                    if func == 'DBG':
                        self.from_debugger(text)
                    elif func == 'WSOUT':
                        what, lenght, text = text.split(':', 2)
                        missing = int(lenght) - len(text)
                        if missing > 0:
                            text += stream.read(missing)
                        if self.panel:
                            if what == 'LOG':
                                self.panel.log_append_text('ws', text)
                            elif what == 'STATUS':
                                self.panel.log_append_text('stdout', text)
                            elif what == 'REQUEST_HEADERS':
                                self.panel.log_append_text('request', text)
                            elif what == 'RESPONSE_HEADERS':
                                self.panel.log_append_text('response', text)

    def trace_line(self, linetext):
        filename, lineno, event = linetext.split('|')
        self.panel.trace_line(lineno, filename)
        self.sb.SetStatusText("debugging")

    def stop_debug(self):
        self.panel.stop_debug()
        self.sb.SetStatusText("stop")
