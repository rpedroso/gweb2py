#!/usr/bin/env python
# coding: utf-8
import os
import cPickle
import shelve

import wx
import wx.lib.flatnotebook as fnb

import dircache
import re
import controls

if USE_VTE:
    import vte
    import gtk
    import gtk.gdk


class Tree(wx.Panel):

    def __init__(self, parent):
        # this is just setup boilerplate
        wx.Panel.__init__(self, parent)
        #self.SetDoubleBuffered(True)

        self.includeDirs = []
        self.excludeDirs = []

        style = wx.TR_DEFAULT_STYLE
        self.tree = wx.TreeCtrl(self, style=style)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpand)

    def OnExpand(self, event):
        '''onExpand is called when the user expands a node on the tree
        object. It checks whether the node has been previously expanded. If
        not, the extendTree function is called to build out the node, which
        is then marked as expanded.'''

        # get the wxID of the entry to expand and check it's validity
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()
        self.rebuild_tree(itemID)

    def GetSelection(self):
        return self.tree.GetSelection()

    def GetPyData(self, item):
        return self.tree.GetPyData(item)

    def rebuild_tree(self, itemID=None):
        wx.BeginBusyCursor()
        if not itemID:
            itemID = self.rootID

        # only build that tree if not previously expanded
        old_pydata = self.tree.GetPyData(itemID)
        # clean the subtree and rebuild it
        self.tree.DeleteChildren(itemID)
        self.extendTree(itemID)
        self.tree.SetPyData(itemID, old_pydata)
        wx.EndBusyCursor()

    def buildTree(self, rootdir):
        '''Add a new root element and then its children'''
        self.rootID = self.tree.AddRoot(os.path.basename(rootdir))
        self.tree.SetPyData(self.rootID, rootdir)
        self.extendTree(self.rootID)
        # on mac cannot expand hidden root
        self.tree.Expand(self.rootID)

    def extendTree(self, parentID):
        '''extendTree is a semi-lazy directory tree builder. It takes
        the ID of a tree entry and fills in the tree with its child
        subdirectories and their children - updating 2 layers of the
        tree. This function is called by buildTree and onExpand methods'''


        # retrieve the associated absolute path of the parent
        parentDir = self.tree.GetPyData(parentID)


        subdirs = dircache.listdir(parentDir)
        #subdirs.sort()
        for child in subdirs:
            child_path = opj(parentDir, child)
            if not os.path.isdir(child_path) and parentID == self.rootID:
                continue
            if child.endswith('.pyc'):
                continue
            if not child.startswith('.') and not os.path.islink(child):
                to_include = False
                if  self.includeDirs and os.path.isdir(child_path):
                    #[child_path p for p in self.includeDirs]
                    for c in self.includeDirs:
                        n = len(c)
                        if c[:n] in child_path:
                            to_include = True
                    if not to_include:
                        continue
                if (self.excludeDirs
                        and os.path.isdir(child_path)
                        and child_path in self.excludeDirs):
                    continue
                # add the child to the parent
                childID = self.tree.AppendItem(parentID, child)
                # associate the full child path with its tree entry
                self.tree.SetPyData(childID, child_path)

                # Now the child entry will show up, but it current has no
                # known children of its own and will not have a '+' showing
                # that it can be expanded to step further down the tree.
                # Solution is to go ahead and register the child's children,
                # meaning the grandchildren of the original parent
                newParent = child
                newParentID = childID
                newParentPath = child_path
                newsubdirs = (dircache.listdir(newParentPath)
                                if os.path.isdir(child_path) else [])
                for grandchild in newsubdirs:
                    grandchild_path = opj(newParentPath, grandchild)
                    if (not child.startswith('.') and not
                            os.path.islink(grandchild_path)):
                        grandchildID = self.tree.AppendItem(newParentID,
                                grandchild)
                        self.tree.SetPyData(grandchildID, grandchild_path)

if USE_VTE:
    FIXED_TABS = 1

    class Terminal(wx.Panel):

        def __init__(self, parent):
            wx.Panel.__init__(self, parent)

            whdl = self.GetHandle()
            window = gtk.gdk.window_lookup(whdl)

            self.pizza = pizza = window.get_user_data()
            self.scrolled_window = scrolled_window = pizza.parent
            scrolled_window.remove(pizza)

            self.ctrl = ctrl = vte.Terminal()
            scrolled_window.add(ctrl)
            scrolled_window.show_all()

            self.ctrl.connect('child-exited', self.run_command_done_callback)
            #self.ctrl.connect('cursor-moved', self.contents_changed_callback)

            emulation = "xterm"
            font = "monospace 8"
            #scrollback = 100
            ctrl.set_emulation(emulation)
            ctrl.set_font_from_string(font)
            #ctrl.set_scrollback_lines(scrollback)
            self.Layout()

        def SetFocus(self):
            self.ctrl.grab_focus()

        def Refresh(self):
            self.ctrl.queue_draw()
            while gtk.events_pending():
                gtk.main_iteration()
            wx.Panel.Refresh(self)

        def run_command(self, command_string):
            '''run_command runs the command_string in the terminal. This
            function will only return when self.thred_running is set to
            True, this is done by run_command_done_callback'''
            command = command_string.split(' ')
            pid = self.ctrl.fork_command(command=command[0],
                                            argv=command,
                                            directory=os.getcwd())
            return pid

        def _remove(self):
            notebook = self.GetParent()
            page_n = notebook.get_selection_by_filename(self.filename)
            notebook.DeletePage(page_n)

        def run_command_done_callback(self, terminal):
            if self.filename == "<shell>":
                self.run_command('bash')
                return

            if self.ctrl.get_child_exit_status() == 0:
                self._remove()
                #wx.CallAfter(self._remove)

        #def capture_text(self, text, text2, text3, text4):
        #    return True

        #def contents_changed_callback(self, terminal):
        #    terminal_text = self.ctrl.get_text(self.capture_text)
        #    #print repr(terminal_text)

    class Editor(Terminal):

        def __init__(self, parent):
            Terminal.__init__(self, parent)

        def quit(self):
            self.ctrl.feed_child(':qall\n')

        def openfile(self, filename, lineno=0):
            current_path = os.getcwd()
            os.chdir(APP_PATH)
            print('vim -ni NONE -X -U NONE +%d %s' % (lineno,
                filename))
            pid = self.run_command('vim -ni NONE -X -U NONE +%d %s' % (lineno,
                filename))

            os.chdir(current_path)
            return pid

        def savefile(self, filename):
            self.ctrl.feed_child(':w\n')

        def trace_line_clear(self):
            self.ctrl.feed_child(':match\n')

        def trace_line(self, lineno):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(":nnoremap <silent> <Leader>l "
                                    "ml:execute 'match Search "
                                    "/\%'.line('.').'l/'\n\l\n")

        def set_break(self, lineno, filename):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(':sign define wholeline linehl=ErrorMsg\n')
            self.ctrl.feed_child(':sign place %d name=wholeline '
                                    'line=%s file=%s\n' % (lineno,
                                        lineno, filename))

        def clear_break(self, lineno):
            self.ctrl.feed_child(':sign unplace %s\n' % lineno)

        def goto_line(self, lineno):
            #print lineno
            self.ctrl.feed_child(':%s\n' % lineno)
else:
    FIXED_TABS = 0
    from editor import Editor


class InfoPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        b = wx.BoxSizer(wx.VERTICAL)
        s = wx.StaticText(self, label="Breakpoints")
        self.bp_list = controls.BPList(self)
        b.Add(s, 0)
        b.Add(self.bp_list, 1, wx.EXPAND, 0)
        self.SetSizer(b)


class LogPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)

        if IS_WIN:
            style = 0
        else:
            style = (fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_SMART_TABS
                 | fnb.FNB_NODRAG | fnb.FNB_NO_X_BUTTON)

        self.notebook = nb = controls.Notebook(self, style=style)

        self.t_ws = t = controls.TextCtrl(nb)
        nb.AddPage(t, "WebServer Logs")

        self.t_stdout = t = controls.TextCtrl(nb)
        nb.AddPage(t, "stdout", select=False)

        self.t_stderr = t = controls.TextCtrl(nb)
        nb.AddPage(t, "stderr", select=False)

        self.t_request = t = controls.TextCtrl(nb)
        nb.AddPage(t, "request", select=False)

        self.t_response = t = controls.TextCtrl(nb)
        nb.AddPage(t, "response", select=False)

        self.t_shell = t = controls.ShellCtrl(nb)
        nb.AddPage(t, "eval shell", select=False)

        b = wx.BoxSizer(wx.HORIZONTAL)
        b.Add(nb, 1, wx.EXPAND, 0)
        self.SetSizer(b)

        self.RE_WS = re.compile("HTTP/\d.\d +(\w+)")

        self.default_text_attr = wx.TextAttr(wx.LIGHT_GREY, wx.NullColour)
        self.t_ws.SetDefaultStyle(wx.TextAttr(wx.LIGHT_GREY, wx.NullColour))
        #wx.Log_SetActiveTarget(wx.LogTextCtrl(t))

    def ws_write(self, t):
        t = t.decode('utf-8', 'replace')
        styles = {
                200: wx.TextAttr(wx.GREEN, wx.NullColour),
                304: wx.TextAttr(wx.BLUE, wx.NullColour),
                404: wx.TextAttr(wx.RED, wx.NullColour),
                }
        s = self.RE_WS.search(t)
        attr = self.default_text_attr
        if s:
            try:
                code = int(s.group(1))
                attr = styles[code]
            except (ValueError, KeyError):
                pass
        self.t_ws.SetDefaultStyle(attr)
        self.t_ws.AppendText(t)

    def stdout_write(self, t):
        t = t.decode('utf-8', 'replace')
        self.t_stdout.AppendText(t)

    def stderr_write(self, t):
        t = t.decode('utf-8', 'replace')
        self.t_stderr.AppendText(t)

    def request_write(self, t):
        t = t.decode('utf-8', 'replace')
        self.t_request.AppendText(t.replace('\r', ''))

    def response_write(self, t):
        t = t.decode('utf-8', 'replace')
        self.t_response.AppendText(t)

    def shell_write(self, t):
        t = t.decode('utf-8', 'replace')
        self.t_shell.AppendText(t)


class BitmapWindow(wx.Window):

    def __init__(self, parent):
        wx.Window.__init__(self, parent, style=wx.FULL_REPAINT_ON_RESIZE)

        self.img = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        if not self.img:
            return
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()

        img = self.img.Copy()
        iw, ih = img.GetSize()

        w, h = self.GetSize()

        factor = min(float(w) / iw, float(h) / ih)
        if factor > 1:
            factor = 1

        rw = iw * factor
        rh = ih * factor

        img.Rescale(iw * factor, ih * factor, wx.IMAGE_QUALITY_HIGH)

        bmp = img.ConvertToBitmap()
        dc.DrawBitmap(bmp, (w - rw) / 2., (h - rh) / 2., True)

    def SetFilenameBitmap(self, filename):
        self.img = wx.Image(filename)
        self.Refresh()


class BitmapInfoPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        b = wx.FlexGridSizer(3, 2)

        #st_filename = wx.StaticText(self, label="filename")
        st_width = wx.StaticText(self, label="width")
        st_height = wx.StaticText(self, label="height")

        #t_filename = wx.TextCtrl(self, style=wx.TE_READONLY)
        t_width = wx.TextCtrl(self, style=wx.TE_READONLY)
        t_height = wx.TextCtrl(self, style=wx.TE_READONLY)

        #self.t_filename = t_filename
        self.t_width = t_width
        self.t_height = t_height

        #b.Add(st_filename)
        #b.Add(t_filename, 1, wx.EXPAND, 0)

        b.Add(st_width)
        b.Add(t_width, 1, wx.EXPAND, 0)

        b.Add(st_height)
        b.Add(t_height, 1, wx.EXPAND, 0)

        b.AddGrowableCol(1)
        self.SetSizer(b)

    def SetInfo(self, img):
        #self.t_filename.SetValue(repr(img))
        w, h = img.GetSize()
        self.t_width.SetValue(str(w))
        self.t_height.SetValue(str(h))


class BitmapPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        b = wx.BoxSizer(wx.VERTICAL)

        self.bmp_win = BitmapWindow(self)
        self.bmp_info = BitmapInfoPanel(self)

        b.Add(self.bmp_win, 1, wx.EXPAND, 0)
        b.Add(self.bmp_info, 0, wx.EXPAND, 0)

        self.SetSizer(b)

    def SetFilenameBitmap(self, filename):
        self.bmp_win.SetFilenameBitmap(filename)
        self.bmp_info.SetInfo(self.bmp_win.img)


class KeyValuePanel(wx.Panel):
    """docstring for KeyValuePanel"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        b = wx.BoxSizer(wx.VERTICAL)
        self.lst = controls.KeyValueList(self)
        b.Add(self.lst, 1, wx.EXPAND, 0)
        self.SetSizer(b)


class MainPanel(wx.Panel):

    def __init__(self, parent, w2p_path):
        wx.Panel.__init__(self, parent)

        self._previous_editor = None
        self.w2p_path = w2p_path

        self.Freeze()
        winids = []

        leftwin = wx.SashLayoutWindow(self,
                style=wx.NO_BORDER | wx.SW_3D)

        leftwin.SetDefaultSize((160, -1))
        leftwin.SetOrientation(wx.LAYOUT_VERTICAL)
        leftwin.SetAlignment(wx.LAYOUT_LEFT)
        leftwin.SetSashVisible(wx.SASH_RIGHT, True)
        leftwin.SetExtraBorderSize(0)
        self.leftwin = leftwin
        winids.append(leftwin.GetId())

        self.tree = t = Tree(leftwin)
        t.buildTree(opj(w2p_path, 'applications'))
        t.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated)

        rightwin = wx.SashLayoutWindow(self,
                style=wx.NO_BORDER | wx.SW_3D)
        rightwin.SetDefaultSize((160, -1))
        rightwin.SetOrientation(wx.LAYOUT_VERTICAL)
        rightwin.SetAlignment(wx.LAYOUT_RIGHT)
        rightwin.SetSashVisible(wx.SASH_LEFT, True)
        self.rightwin = rightwin
        winids.append(rightwin.GetId())
        self.info = InfoPanel(rightwin)
        rightwin.Hide()

        bottomwin = wx.SashLayoutWindow(self,
                style=wx.NO_BORDER | wx.SW_3D)
        bottomwin.SetDefaultSize((-1, 150))
        bottomwin.SetOrientation(wx.LAYOUT_HORIZONTAL)
        bottomwin.SetAlignment(wx.LAYOUT_BOTTOM)
        bottomwin.SetSashVisible(wx.SASH_TOP, True)
        self.bottomwin = bottomwin
        winids.append(bottomwin.GetId())

        self.log = LogPanel(bottomwin)

        if IS_WIN:
            style = 0
        else:
            style = (fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS
                     | fnb.FNB_X_ON_TAB | fnb.FNB_SMART_TABS
                     | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_NODRAG)
        self.notebook = nb = controls.Notebook(self, style=style)
        if USE_VTE:
            self.terminal = Terminal(nb)
            self.terminal.page_idx = self.notebook.GetPageCount()
            self.terminal.filename = '<shell>'
            self.terminal.run_command('bash')
            self.terminal.ctrl.feed_child('PS1="web2py@\W\$ "\n')
            self.terminal.ctrl.feed_child('')
            nb.AddPage(self.terminal, "Shell")

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(
            wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag,
            id=min(winids), id2=max(winids))
        self.notebook.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        if not IS_WIN:
            self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_notebook_page_closing)

        self.Thaw()

    def Layout(self):
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)

    def OnSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)
        event.Skip()

    def OnSashDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        eobj = event.GetEventObject()

        if eobj is self.leftwin:
            self.leftwin.SetDefaultSize((event.GetDragRect().width, -1))
        elif eobj is self.rightwin:
            self.rightwin.SetDefaultSize((event.GetDragRect().width, -1))
        elif eobj is self.bottomwin:
            self.bottomwin.SetDefaultSize((-1, event.GetDragRect().height))

        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)
        self.notebook.Refresh()

    def OnRightUp(self, evt):
        print 'right_up'
        idx, flags = self.notebook.HitTest((evt.m_x, evt.m_y))
        if idx != wx.NOT_FOUND:
            self.notebook_close_tab(idx)
        else:
            evt.Skip()

    # FIXME: should be an event
    def signal_can_close_tab(self, n):
        self.notebook_close_tab(n)

    def on_notebook_page_closing(self, evt):
        page = self.notebook.GetPage(evt.GetSelection())
        if isinstance(page, Editor):
            if page.is_dirty():
                evt.Veto()
            else:
                evt.Skip()
        else:
            evt.Skip()

    def ClosePanel(self, cb):
        children = list(self.notebook.GetChildren())
        # need to order by desc
        # to avoid pages index changes
        #pages = range(len(children))
        #pages.reverse()
        #for i in pages:
        #    vim = pages[i]
        #    if isinstance(vim, Editor):
        #        vim.quit()
        #    else:
        #        #self.notebook.DeletePage(i)
        #        self.notebook_close_tab(i)
        for i, page in enumerate(children):
            if not isinstance(page, Editor):
                self.notebook_close_tab(i)

        children = list(self.notebook.GetChildren())
        for page in children:
            if isinstance(page, Editor):
                page.quit()

        #wx.SafeYield()
        #import time
        #time.sleep(.2)
        #wx.SafeYield()

        if USE_VTE:
            while gtk.events_pending():
                gtk.main_iteration()

        if self.notebook.GetPageCount() <= FIXED_TABS:
            cb(True)
        else:
            cb(False)

    def OnActivated(self, evt):
        t = evt.GetEventObject()
        item = evt.GetItem()
        if item:
            ndir = t.GetPyData(item)
            self.open_tab(ndir, get_dir_file(ndir))
        evt.Skip()

    def is_debug_on(self):
        return self.rightwin.IsShown()

    def open_tab(self, ndir, itemtext, lineno=0):
        ndir = os.path.abspath(ndir)
        if IS_WIN:
            ndir = ndir.lower()
        ndir_isfile = os.path.isfile(ndir)
        if (ndir_isfile
                and os.path.splitext(ndir.lower())[-1] in ('.py', '.html',
                    '.css', '.js', '.load', '.xml', '.json', '.rss')):
            if ndir in self.notebook:
                self.notebook.set_selection_by_filename(ndir)
                if lineno > 0:
                    self.notebook.GetCurrentPage().goto_line(lineno)
            else:
                editor = Editor(self.notebook)
                editor.page_idx = self.notebook.GetPageCount()
                editor.filename = ndir
                self.notebook.AddPage(editor, itemtext)
                self.notebook.set_selection_by_filename(ndir)
                pid = editor.openfile(ndir, lineno)
                editor.pid = pid

                editor.Refresh()

                editor.SetFocus()

        elif (ndir_isfile and os.path.dirname(ndir).endswith('sessions')):
            self.open_sessionfile(ndir, itemtext)
        elif (ndir_isfile and os.path.dirname(ndir).endswith('cache')):
            self.open_cachefile(ndir, itemtext)
        elif (ndir_isfile and os.path.dirname(ndir).endswith('errors')):
            self.open_errorfile(ndir, itemtext)
        elif (ndir_isfile
                and os.path.splitext(ndir.lower())[-1] in ('.png', '.jpg',
                    '.gif', '.ico')):
            self.open_image(ndir, itemtext)
        elif os.path.isdir(ndir):
            if USE_VTE:
                self.terminal.ctrl.feed_child('\ncd %s\n' % ndir)

    def open_image(self, ndir, itemtext):
        if '<image>' in self.notebook:
            self.notebook.set_selection_by_filename('<image>')
            sbmp = self.notebook.GetCurrentPage()
            sbmp.SetFilenameBitmap(ndir)
            sbmp.filename = '<image>'
            self.notebook.SetPageText(sbmp.page_idx, itemtext)
        else:
            sbmp = BitmapPanel(self.notebook)
            sbmp.SetFilenameBitmap(ndir)
            sbmp.page_idx = self.notebook.GetPageCount()
            sbmp.filename = '<image>'
            self.notebook.AddPage(sbmp, itemtext)
            self.notebook.SetSelection(sbmp.page_idx)

    def open_sessionfile(self, ndir, itemtext):
        if '<sessionfile>' in self.notebook:
            self.notebook.set_selection_by_filename('<sessionfile>')
            page = self.notebook.GetCurrentPage()
            f = open(ndir, 'rb')
            data = cPickle.load(f)
            f.close()
            page.lst.data = data.items()
            page.filename = '<sessionfile>'
            self.notebook.SetPageText(page.page_idx, itemtext)
        else:
            page = KeyValuePanel(self.notebook)
            f = open(ndir, 'rb')
            data = cPickle.load(f)
            f.close()
            page.lst.data = data.items()
            page.page_idx = self.notebook.GetPageCount()
            page.filename = '<sessionfile>'
            self.notebook.AddPage(page, itemtext)
            self.notebook.SetSelection(page.page_idx)

    def open_cachefile(self, ndir, itemtext):
        if '<cachefile>' in self.notebook:
            self.notebook.set_selection_by_filename('<cachefile>')
            page = self.notebook.GetCurrentPage()
            f = shelve.open(ndir)
            page.lst.data = f.items()
            f.close()
            page.filename = '<cachefile>'
            self.notebook.SetPageText(page.page_idx, itemtext)
        else:
            page = KeyValuePanel(self.notebook)
            f = shelve.open(ndir)
            page.lst.data = f.items()
            f.close()
            page.page_idx = self.notebook.GetPageCount()
            page.filename = '<cachefile>'
            self.notebook.AddPage(page, itemtext)
            self.notebook.SetSelection(page.page_idx)

    def open_errorfile(self, ndir, itemtext):
        import errorpanel
        f = open(ndir, 'rb')
        if '<errorfile>' in self.notebook:
            self.notebook.set_selection_by_filename('<errorfile>')
            page = self.notebook.GetCurrentPage()
        else:
            page = errorpanel.ErrorPanel(self.notebook, self)
            page.page_idx = self.notebook.GetPageCount()
            self.notebook.AddPage(page, 'Error')
            self.notebook.SetSelection(page.page_idx)

        page.filename = '<errorfile>'
        page.set_error(errorpanel.Error(cPickle.load(f)))
        f.close()

    # FIXME: Called from errorpanel. Make it an event
    def JumpToLine(self, line, ndir):
        self.open_tab(ndir, get_dir_file(ndir), line)

    def set_break(self, lineno):
        editor = self.notebook.GetCurrentPage()
        filename = editor.filename
        if (str(lineno), filename) in self.info.bp_list._bp_list:
            self.info.bp_list.remove((str(lineno), filename))
            return None
        editor.set_break(lineno, filename)
        self.info.bp_list.append((str(lineno), filename))
        return filename

    def clear_break(self, lineno, filename):
        self.open_tab(filename, get_dir_file(filename))
        editor = self.notebook.GetCurrentPage()
        editor.clear_break(lineno)

    def trace_line(self, lineno, filename):
        if self._previous_editor:
            self._previous_editor.trace_line_clear()

        self.open_tab(filename, get_dir_file(filename))

        editor = self.notebook.GetCurrentPage()
        self._previous_editor = editor
        editor.trace_line(lineno)

    def stop_debug(self):
        if self._previous_editor:
            self._previous_editor.trace_line_clear()

    def app_new(self, name):
        # Fake a request
        from gluon.admin import app_create
        from gluon.globals import Request
        request = Request()
        request.folder = opj(self.w2p_path, 'applications', 'admin')

        ret = app_create(name, request)
        if ret:
            self.tree.rebuild_tree()
            return ret
        import errno
        raise IOError(errno.ENOENT, "'welcome.w2p' probably missing",
                opj(self.w2p_path, 'welcome.w2p'))

    def app_debug_mode(self, debug=True):
        self.rightwin.Show(not self.rightwin.IsShown())
        self.Layout()

    # Notebook interface
    def notebook_is_editor(self):
        editor = self.notebook.GetCurrentPage()
        return isinstance(editor, Editor)

    def notebook_new_file(self, filename):
        self.open_tab(filename, get_dir_file(filename))

    def notebook_open_file(self, filename):
        self.open_tab(filename, get_dir_file(filename))

    def notebook_save_file(self):
        editor = self.notebook.GetCurrentPage()
        if isinstance(editor, Editor):
            editor.savefile(editor.filename)

    def notebook_close_current_tab(self):
        idx = self.notebook.GetSelection()
        self.notebook_close_tab(idx)

    def notebook_close_tab(self, idx):
        self.notebook.DeletePage(idx)
        #self.Refresh()

    def notebook_setfocus(self):
        self.notebook.SetFocus()

    def notebook_advance(self, direction=True):
        self.notebook.AdvanceSelection(direction)

    # Tree interface
    def tree_setfocus(self):
        self.tree.SetFocus()

    def tree_get_selected_item_data(self):
        item = self.tree.GetSelection()
        if item.IsOk():
            return self.tree.GetPyData(item)
        return None

    # LogPanel interface
    def log_clear_current(self):
        ctrl = self.log.notebook.GetCurrentPage()
        ctrl.Clear()

    def log_append_text(self, where, text):
        method = getattr(self.log, '%s_write' % where)
        if method:
            method(text)
