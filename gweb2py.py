#!/usr/bin/env python
# coding: utf-8

import os, sys
os.putenv('WINGDB_ACTIVE', '1')

try:
    USE_VTE = True
    # test an import failure
    #import zzzzzzzzzz
    import gobject
    gobject.threads_init()

    import vte
    import pygtk
    pygtk.require('2.0')
    import gtk, gtk.gdk
except ImportError:
    USE_VTE = False

import wx
import wx.lib.dialogs
import wx.lib.mixins.listctrl as listmix

import dircache
import re

opj = os.path.join

APP_PATH = os.path.realpath(os.path.dirname(__file__))

PORT = 8000
IS_MAC = 'wxMac' in wx.PlatformInfo

def get_dir_file(filepath):
    filepath_list = filepath.split(os.sep)
    for d in ('controllers', 'views', 'models',
            'static', 'uploads', 'modules'):
        if d in filepath_list:
            idx = filepath_list.index(d) + 1
            return '[%s]%s' % (d[0].upper(), opj(*filepath_list[idx:]))
    return filepath_list[-1]

myEVT_BPLIST_REMOVE = wx.NewEventType()
EVT_BPLIST_REMOVE = wx.PyEventBinder(myEVT_BPLIST_REMOVE, 1)
class MyEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.myVal = ()

    def SetMyVal(self, val):
        self.myVal = val

    def GetMyVal(self):
        return self.myVal

class BPList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent,
            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES#|wx.LC_SINGLE_SEL
            )
        listmix.ListCtrlAutoWidthMixin.__init__(self)


        self._bp_list = []
        self._tooltips = []

        self.InsertColumn(0, "Line")
        self.InsertColumn(1, "Filename")
        self.SetColumnWidth(0, 45)
        self.SetColumnWidth(1, 300)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def OnLeaveWindow(self, evt):
        self.SetToolTip(wx.ToolTip(' '))
        evt.Skip()

    def OnMotion(self, evt):
        #totalWidth=0
        #tmpWidth=0
        #flags = wx.LIST_HITTEST_ONITEM
        row, where = self.HitTest((evt.m_x, evt.m_y))
        #for i in range(self.GetColumnCount()):
        #    tmpWidth = self.GetColumnWidth(i)
        #    totalWidth += tmpWidth
        #    if evt.m_x < totalWidth:
        #        col = i
        #        break

        if row>-1: # and col>-1:
            tip = self._tooltips[row] #self.GetTooltip(row, col)
            self.SetToolTip(wx.ToolTip(tip))
        evt.Skip()

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        #print("OnItemActivated: %s\nTopItem: %s\n" %
        #                   (self.GetItemText(self.currentItem), self.GetTopItem()))
        lineno = self.GetItemText(self.currentItem)
        filename = self.getColumnText(self.currentItem, 1)
        self.remove((lineno, filename))

    def OnGetItemText(self, item, col):
        return self._bp_list[item][col]

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def append(self, bp):
        #print >>sys.stderr, repr(bp)
        self._bp_list.append(bp)
        self._tooltips.append(bp[1])
        self.SetItemCount(len(self._bp_list))
        #print >>sys.stderr, repr(self._bp_list)

    def remove(self, bp):
        #print >>sys.stderr, repr(bp)
        #print >>sys.stderr, repr(self._bp_list)
        self._bp_list.remove(bp)
        self._tooltips.remove(bp[1])
        self.SetItemCount(len(self._bp_list))
        evt = MyEvent(myEVT_BPLIST_REMOVE, self.GetId())
        evt.SetMyVal(bp)
        self.GetEventHandler().ProcessEvent(evt)

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
            self.process.Kill(self.pid, wx.SIGTERM)

        self.is_running = False

    def start(self, passwd, port):
        self.process = wx.Process(self.parent)
        self.process.Redirect()
        p = self.app_path
        #os.putenv('WINGDB_ACTIVE', "1")
        sys.path.insert(0, self.w2p_path)

        os.chdir(self.w2p_path)

        if not os.path.isfile('web2py.py'):
            self.process = None
            raise Exception('%s: Execution failed' % 'web2py.py')

        passwd = passwd.strip()
        if passwd:
            from gluon.main import save_password
            save_password(passwd, port)

        #cmd = 'python -u ./web2py.py -a "%s"' % passwd
        cmd = '%s -u %s %s %s' % (sys.executable, opj(p, 'gw2pserver.py'), port, self.w2p_path)
        #print >>sys.stderr, 'cmd:', cmd
        #cmd = 'python -u %s' % os.path.join(p, 'w2pdbg.py')

        self.pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)

        if self.pid == 0:
            self.process = None
            raise Exception('%s: Execution failed' % 'web2py.py')
        self.is_running = True

class Tree(wx.Panel):
    def __init__(self, parent):
        # this is just setup boilerplate
        wx.Panel.__init__(self, parent)

        self.includeDirs=[]
        self.excludeDirs=[]

        style = wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS
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

    def rebuild_tree(self, itemID=None):
        if not itemID:
            itemID = self.rootID

        # only build that tree if not previously expanded
        old_pydata = self.tree.GetPyData(itemID)
        if 1: #old_pydata[1] == False:
            # clean the subtree and rebuild it
            self.tree.DeleteChildren(itemID)
            self.extendTree(itemID)
            self.tree.SetPyData(itemID, old_pydata)

    def buildTree(self, rootdir):
        '''Add a new root element and then its children'''
        self.rootID = self.tree.AddRoot(os.path.basename(rootdir))
        self.tree.SetPyData(self.rootID, rootdir)
        self.extendTree(self.rootID)
	# on mac cannot expand hidden root
        #self.tree.Expand(self.rootID)

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
            if child.endswith('.pyc'): continue
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
                if self.excludeDirs and os.path.isdir(child_path) and child_path in self.excludeDirs:
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
                newsubdirs = dircache.listdir(newParentPath) if os.path.isdir(child_path) else []
                #newsubdirs.sort()
                for grandchild in newsubdirs:
                    grandchild_path = opj(newParentPath, grandchild)
                    #if os.path.isdir(grandchild_path) and not os.path.islink(grandchild_path):
                    if not child.startswith('.') and not os.path.islink(grandchild_path):
                        grandchildID = self.tree.AppendItem(newParentID, grandchild)
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

        #    self.Bind(wx.EVT_SIZE, self.OnSize)

        #def OnSize(self, evt):
        #    print evt.Size
        #    self.ctrl.queue_draw()
        #    self.ctrl.set_size_request(*evt.Size)

        def SetFocus(self):
            self.ctrl.grab_focus()

        def Refresh(self):
            self.ctrl.queue_draw()
            while gtk.events_pending(): gtk.main_iteration()
            wx.Panel.Refresh(self)

        def run_command(self, command_string):
            '''run_command runs the command_string in the terminal. This
            function will only return when self.thred_running is set to
            True, this is done by run_command_done_callback'''
            command = command_string.split(' ')
            pid =  self.ctrl.fork_command(command=command[0], argv=command, directory=os.getcwd())
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

        def openfile(self, filename):
            current_path = os.getcwd()
            os.chdir(APP_PATH)
            #--noplugin -ni NONE -u vim/gweb2py.vim -X -U NONE
            #pid = self.run_command('vim --noplugin -u %s -ni NONE %s -X -U NONE' %
            pid = self.run_command('vim -ni NONE %s -X -U NONE' %
                #(os.path.join(APP_PATH, "vim", "gweb2py.vim"),
                filename)
                #)
            os.chdir(current_path)
            return pid

        def savefile(self, filename):
            self.ctrl.feed_child(':w\n')

        def trace_line_clear(self):
            self.ctrl.feed_child(':match\n')

        def trace_line(self, lineno):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(":nnoremap <silent> <Leader>l ml:execute 'match Search /\%'.line('.').'l/'\n\l\n")

        def set_break(self, lineno, filename):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(':sign define wholeline linehl=ErrorMsg\n')
            self.ctrl.feed_child(':sign place %d name=wholeline line=%s file=%s\n' % (lineno, lineno, filename))

        def clear_break(self, lineno):
            self.ctrl.feed_child(':sign unplace %s\n' % lineno)

else:
    FIXED_TABS = 0
    from editor import Editor

#class Flash(wx.PopupWindow):
#    def __init__(self, parent):
#        wx.PopupWindow.__init__(self, parent)
#        self.SetBackgroundColour("CADET BLUE")
#
#        st = wx.StaticText(self, -1,
#                          "This is a special kind of top level\n"
#                          "window that can be used for\n"
#                          "popup menus, combobox popups\n"
#                          "and such.\n\n"
#                          "Try positioning the demo near\n"
#                          "the bottom of the screen and \n"
#                          "hit the button again.\n\n"
#                          "In this demo this window can\n"
#                          "be dragged with the left button\n"
#                          "and closed with the right."
#                          ,
#                          pos=(10,10))
#
#        sz = st.GetBestSize()
#        self.SetSize( (sz.width+20, sz.height+20) )
#
#        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
#
#        w, h = parent.GetSize()
#        self.Position((0,50), (w-sz.width, 50))
#
#        self.Show()
#        wx.CallAfter(self.Refresh)
#        wx.CallLater(2000, self.OnMouseLeftUp)
#
#    def OnMouseLeftUp(self, evt=None):
#        self.Show(False)
#        self.Destroy()

class InfoPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        b = wx.BoxSizer(wx.VERTICAL)
        s = wx.StaticText(self, label="Breakpoints")
        self.bp_list = BPList(self)
        b.Add(s, 0) #, wx.EXPAND, 0)
        b.Add(self.bp_list, 1, wx.EXPAND, 0)
        self.SetSizer(b)

class TextCtrl(wx.TextCtrl):
    def __init__(self, parent,
            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.TE_RICH2):
        wx.TextCtrl.__init__(self, parent, style=style)
	if not IS_MAC:
            self.SetBackgroundColour(wx.BLACK)
            self.SetForegroundColour(wx.WHITE)
            self.SetFont(wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False))

class ShellCtrl(TextCtrl):
    def __init__(self, parent):
        self._prompt = '> '
        style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_RICH2|wx.TE_PROCESS_ENTER
        TextCtrl.__init__(self, parent, style)
        self.set_prompt()
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

    def set_prompt(self):
        #self.AppendText(self._prompt)
        TextCtrl.AppendText(self, self._prompt)

    def send_command(self, text):
        text = text.strip()
        if text:
            self.GetTopLevelParent().shell_command(text)
        else:
            wx.CallAfter(self.set_prompt)

    def GetNumberOfLines(self):
	n = TextCtrl.GetNumberOfLines(self)
        if IS_MAC:
            return n - 1
        return n

    def OnEnter(self, evt):
        self.SetInsertionPointEnd()
        text = self.GetLineText(self.GetNumberOfLines()-1).lstrip(self._prompt)
	print 'OnEnter', repr(text)
        self.send_command(text)
        evt.Skip()

    def AppendText(self, text):
        text = text.strip()
        if (text.startswith('<Storage {')
                or text.startswith('<Row {')
                or text.startswith('<DAL {')):
            text = text.split(', ')
            text = ',\n'.join(text)
        text = "%s\n" % text
        TextCtrl.AppendText(self, text)
        wx.CallAfter(self.set_prompt)

class Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, style=wx.NB_MULTILINE)

    def __contains__(self, o):
        for c in self.GetChildren():
            if c.filename == o:
                return True
        return False

    def get_selection_by_filename(self, name):
        for i, c in enumerate(self.GetChildren()):
            if c.filename == name:
                return i
        return -1

    def set_selection_by_filename(self, name):
        i = self.get_selection_by_filename(name)
        if i > -1:
            self.SetSelection(i)

    def SetFocus(self):
        idx = self.GetSelection()
        self.GetChildren()[idx].SetFocus()

    def DeletePage(self, idx):
        w = self.GetPage(idx)
        if w.filename in ('<shell>',):
            return
        wx.Notebook.DeletePage(self, idx)

class LogPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)

        self.notebook = nb = Notebook(self)

        self.t_ws = t = TextCtrl(nb)
        nb.AddPage(t, "WebServer Logs")

        self.t_stdout = t = TextCtrl(nb)
        nb.AddPage(t, "stdout")

        self.t_stderr = t = TextCtrl(nb)
        nb.AddPage(t, "stderr")

        self.t_request = t = TextCtrl(nb)
        nb.AddPage(t, "request")

        self.t_response = t = TextCtrl(nb)
        nb.AddPage(t, "response")

        self.t_shell = t = ShellCtrl(nb)
        nb.AddPage(t, "eval shell")

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
        self.t_request.AppendText(t)

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
        #self.img = wx.Image(filename)
        #self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    #def OnSize(self, evt):
    #    self.Refresh()

    def OnPaint(self, evt):
        if not self.img:
            return
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()

        img = self.img.Copy()
        iw, ih = img.GetSize()

        w, h = self.GetSize()

        factor = min(float(w)/iw, float(h)/ih)
        if factor > 1:
            factor = 1

        rw = iw * factor
        rh = ih * factor

        img.Rescale(iw*factor, ih*factor, wx.IMAGE_QUALITY_HIGH)
        #img = img.ResampleBox(rw, rh)

        bmp = img.ConvertToBitmap()
        dc.DrawBitmap(bmp, (w-rw)/2., (h-rh)/2., True)

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
        #XXX: print dir(img)
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

    #def SetProps(self, props={}):
    #    for k in props.keys():
    #        p = getattr(self.bmp_info, 't_%s' % k)
    #        if p:
    #            p.SetValue(props[k])

class MainPanel(wx.Panel):
    def __init__(self, parent, w2p_path):
        wx.Panel.__init__(self, parent)

        winids = []

        leftwin =  wx.SashLayoutWindow(
                self, -1, wx.DefaultPosition, (200, 30),
                wx.NO_BORDER|wx.SW_3D
                )

        leftwin.SetDefaultSize((160, 1000))
        leftwin.SetOrientation(wx.LAYOUT_VERTICAL)
        leftwin.SetAlignment(wx.LAYOUT_LEFT)
        leftwin.SetSashVisible(wx.SASH_RIGHT, True)
        leftwin.SetExtraBorderSize(0)
        self.leftwin = leftwin
        winids.append(leftwin.GetId())

        self.tree = t = Tree(leftwin)
        #t.includeDirs = [os.path.join(w2p_path, d)
        #                   for d in ['models', 'views', 'controllers', 'modules', 'static']]
        t.buildTree(opj(w2p_path, 'applications'))
        t.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated)

        rightwin = wx.SashLayoutWindow(self,
                style=wx.NO_BORDER|wx.SW_3D
                )
        rightwin.SetDefaultSize((160, 1000))
        rightwin.SetOrientation(wx.LAYOUT_VERTICAL)
        rightwin.SetAlignment(wx.LAYOUT_RIGHT)
        rightwin.SetSashVisible(wx.SASH_LEFT, True)
        self.rightwin = rightwin
        winids.append(rightwin.GetId())
        self.info = InfoPanel(rightwin)
        rightwin.Hide()

        bottomwin = wx.SashLayoutWindow(self,
                style=wx.NO_BORDER|wx.SW_3D
                )
        bottomwin.SetDefaultSize((1000, 150))
        bottomwin.SetOrientation(wx.LAYOUT_HORIZONTAL)
        bottomwin.SetAlignment(wx.LAYOUT_BOTTOM)
        bottomwin.SetSashVisible(wx.SASH_TOP, True)
        self.bottomwin = bottomwin
        winids.append(bottomwin.GetId())

        self.log = LogPanel(bottomwin)

        self.notebook = nb = Notebook(self)
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
            id=min(winids), id2=max(winids)
            )

    def OnSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)
	event.Skip()

    def OnSashDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            #self.log.write('drag is out of range')
            return

        eobj = event.GetEventObject()

        if eobj is self.leftwin:
            self.leftwin.SetDefaultSize((event.GetDragRect().width, 1000))
        elif eobj is self.rightwin:
            self.rightwin.SetDefaultSize((event.GetDragRect().width, 1000))
        elif eobj is self.bottomwin:
            self.bottomwin.SetDefaultSize((1000, event.GetDragRect().height))

        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)
        self.notebook.Refresh()

    def ClosePanel(self, cb):
        vims = list(self.notebook.GetChildren())
        for i, vim in enumerate(vims):
            if isinstance(vim, Editor):
                vim.quit()
            else:
                self.notebook.DeletePage(i)

            #wx.SafeYield()
        wx.SafeYield()
        #evt = wx.EventLoop.GetActive()
        #while evt.Pending():
        #    evt.Dispatch()
        import time
        time.sleep(.2)
        wx.SafeYield()

        if USE_VTE:
            while gtk.events_pending(): gtk.main_iteration()

        if self.notebook.GetPageCount() <= FIXED_TABS:
            cb(True)
        else:
            cb(False)


    def OnActivated(self, evt):
        t = evt.GetEventObject()
        item = evt.GetItem()
        if item:
            ndir = t.GetPyData(item)
            #print ndir
            #itemtext = t.GetItemText(item)
            #self.open_tab(ndir, itemtext)
            self.open_tab(ndir, get_dir_file(ndir))
        evt.Skip()

    def open_tab(self, ndir, itemtext):
	ndir = os.path.abspath(ndir)
        ndir_isfile = os.path.isfile(ndir)
        if ndir_isfile and os.path.splitext(ndir.lower())[-1] in ('.py', '.html', '.css', '.js', '.load', '.xml', '.json', '.rss'):
            if ndir in self.notebook:
                self.notebook.set_selection_by_filename(ndir)
            else:
                editor = Editor(self.notebook)
                editor.page_idx = self.notebook.GetPageCount()
                editor.filename = ndir
                self.notebook.AddPage(editor, itemtext)
                self.notebook.set_selection_by_filename(ndir)
                #pid = editor.run_command('vim -u %s -ni NONE %s' % (os.path.join(APP_PATH, "vim", "myvimrc"), ndir))
                pid = editor.openfile(ndir)
                editor.pid = pid

                editor.Refresh()

                editor.SetFocus()

        elif ndir_isfile and os.path.splitext(ndir.lower())[-1] in ('.png', '.jpg', '.gif', '.ico'):
            self.open_image(ndir, itemtext)
        elif os.path.isdir(ndir):
            self.terminal.ctrl.feed_child('\ncd %s\n' % ndir)
            #self.terminal.ctrl.feed_child('')

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

class Frame(wx.Frame):
    def __init__(self, parent , size, w2p_path=None):
        wx.Frame.__init__(self, parent, size=size, title="gweb2py")

        self.server = None
        self.panel = None
        self.w2p_path = w2p_path
        self.previous_editor = None

        #Build menus
        menuBar = wx.MenuBar()

        menu = wx.Menu()
        item1 = menu.Append(wx.ID_ANY, "&New", "")
        item2 = menu.Append(wx.ID_ANY, "&Open", "")
        item3 = menu.Append(wx.ID_ANY, "&Close", "")
        menuBar.Append(menu, "&Application")

        self.Bind(wx.EVT_MENU, self.OnMenuAppNew, item1)
        self.Bind(wx.EVT_MENU, self.OnMenuAppOpen, item2)
        self.Bind(wx.EVT_MENU, self.OnMenuAppClose, item3)

        menu = wx.Menu()
        #item1 = menu.Append(wx.ID_ANY, "&New", "")
        #item2 = menu.Append(wx.ID_ANY, "&Open", "")
        item3 = menu.Append(wx.ID_ANY, "&Save\tCtrl-S", "Save current file")
        #item4 = menu.Append(wx.ID_ANY, "&Close", "")
        menuBar.Append(menu, "&File")

        #self.Bind(wx.EVT_MENU, self.OnMenuFileNew, item1)
        #self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, item2)
        self.Bind(wx.EVT_MENU, self.OnMenuFileSave, item3)
        #self.Bind(wx.EVT_MENU, self.OnMenuFileClose, item4)

        menu = wx.Menu()
        item1 = menu.Append(wx.ID_ANY, "Focus file &browser\tCtrl+1", "Set focus to file browser window")
        item2 = menu.Append(wx.ID_ANY, "Focus &editor\tCtrl+2", "Set focus to current editor window")
        item3 = menu.Append(wx.ID_ANY, "&Previous tab\tCtrl+PageUp", "Previous tab")
        item4 = menu.Append(wx.ID_ANY, "&Next tab\tCtrl+PageDown", "Next tab")
        item5 = menu.Append(wx.ID_ANY, "&Close tab\tCtrl+4", "Close current tab.")
        ID6=wx.NewId()
        item6 = menu.Append(ID6, "&Clear current output window\tCtrl+K", "Clear contents of current output window")
        menuBar.Append(menu, "&Windows")

        self.Bind(wx.EVT_MENU, self.OnMenuFocusFileBrowser, item1)
        self.Bind(wx.EVT_MENU, self.OnMenuFocusNotebook, item2)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowsPrev, item3)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowsNext, item4)
        self.Bind(wx.EVT_MENU, self.OnMenuCloseTab, item5)
        self.Bind(wx.EVT_MENU, self.OnMenuWindowClear, item6)

        self.menu_debug = wx.Menu()
	if IS_MAC:
            self.f2 = self.menu_debug.Append(wx.ID_ANY, "&Enable/Disable debug\tCtrl+F2", "Turn debugger on or off")
            self.f3 = self.menu_debug.Append(wx.ID_ANY, "&Add/Remove breakpoint...\tCtrl+F3", "Add or remove breakpoint...")
            self.f4 = self.menu_debug.Append(wx.ID_ANY, "&Enable/Disable gluon debug \tCtrl+F4", "Allow debugging web2py gluon code")
            self.f6 = self.menu_debug.Append(wx.ID_ANY, "&Continue\tCtrl+F6", "Continue to next breakpoint or until the end")
            self.f7 = self.menu_debug.Append(wx.ID_ANY, "&Debug step\tCtrl+F7", "Stop after one line of code.")
            self.f8 = self.menu_debug.Append(wx.ID_ANY, "&Debug next\tCtrl+F8", "Stop on the next line in or below the given frame.")
            self.f9 = self.menu_debug.Append(wx.ID_ANY, "&Debug until\tCtrl+F9", "Stop when the line with the line number greater than the current one is reached or when returning from current frame")
	else:
            self.f2 = self.menu_debug.Append(wx.ID_ANY, "&Enable/Disable debug\tF2", "Turn debugger on or off")
            self.f3 = self.menu_debug.Append(wx.ID_ANY, "&Add/Remove breakpoint...\tF3", "Add or remove breakpoint...")
            self.f4 = self.menu_debug.Append(wx.ID_ANY, "&Enable/Disable gluon debug \tF4", "Allow debugging web2py gluon code")
            self.f6 = self.menu_debug.Append(wx.ID_ANY, "&Continue\tF6", "Continue to next breakpoint or until the end")
            self.f7 = self.menu_debug.Append(wx.ID_ANY, "&Debug step\tF7", "Stop after one line of code.")
            self.f8 = self.menu_debug.Append(wx.ID_ANY, "&Debug next\tF8", "Stop on the next line in or below the given frame.")
            self.f9 = self.menu_debug.Append(wx.ID_ANY, "&Debug until\tF9", "Stop when the line with the line number greater than the current one is reached or when returning from current frame")
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
        #self.Bind(wx.EVT_MENU, self.OnMenuDebugEval, item6)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugAllowGluon, self.f4)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugAddBP, self.f3)

        # Bind breakpoint event to remove breakpoints on double click
        self.Bind(EVT_BPLIST_REMOVE, self.OnBPRemove)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_IDLE, self.OnTimer)

        self.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

        #self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

        self.Show()

        if self.w2p_path:
            self.AppOpen()

    #def OnUpdateUI(self, evt):
    #    self.ToggleMenuDebugItems()
    #    #self.OnTimer(None)
    #    #if not self.panel:
    #    #    self.ToggleMenuDebugItems()
    #    #    return
    #    #else:
    #    #    #print 'app opened',
    #    #    pass
    #    #if self.server and self.server.process is not None:
    #    #    if self.panel.rightwin.IsShown(): # Debug enabled
    #    #        #print 'debug enabled',
    #    #        self.ToggleMenuDebugItems()
    #    #        pass
    #    #    else:
    #    #        #print 'debug disabled',
    #    #        self.ToggleMenuDebugItems()
    #    #        pass

    def ToggleMenuDebugItems(self):
        #print 'aqui'
        items = ['f3', 'f4', 'f6', 'f7', 'f8', 'f9']
        #if self.panel:
        #    print self.panel
        #    print self.panel.rightwin.IsShown()
        if self.panel and self.panel.rightwin.IsShown(): # Debug enabled
            for item in items:
                self.menu_debug.Enable(getattr(self, item).GetId(), True)
        else:
            for item in items:
                self.menu_debug.Enable(getattr(self, item).GetId(), False)

    def OnRightUp(self, evt):
        idx, flags = self.panel.notebook.HitTest((evt.m_x, evt.m_y))
        if idx != wx.NOT_FOUND:
            self.CloseTab(idx)
        else:
            evt.Skip()

    def OnProcessEnded(self, evt):
        if self.panel:
            self.OnTimer(None)
            self.panel.log.stdout_write("webserver stopped")
        self.server.process.Destroy()
        self.server.process = None
        self.server = None

    def ChooseApp(self):
        dirpath = None
        dlg = wx.DirDialog(self, "Choose a directory",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           | wx.DD_CHANGE_DIR
                           )

        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            self.w2p_path = dirpath

        dlg.Destroy()
        return bool(dirpath)

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
        #else:
        #    Flash(self)

    def AppOpen(self):
        if not self.w2p_path:
            if not self.ChooseApp():
                return

        self.w2p_path = os.path.normpath(self.w2p_path)
        self.server = Web2pyServer(self, APP_PATH, self.w2p_path)
        p = self.AskPassword()
        try:
            self.server.start(p, PORT)
        except Exception, e:
            wx.MessageDialog(self, 'Not a web2py directory\n%s' % repr(e), "error").ShowModal()
            return

        os.chdir(self.w2p_path)
        self.panel = MainPanel(self, self.w2p_path)
        self.panel.notebook.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Layout()
        self.SendSizeEvent()
        self.timer.Start(500)

    def OnMenuAppNew(self, evt):
        if not self.panel:
            if not self.ChooseApp():
                return
        p = None
        dlg = wx.TextEntryDialog(self, 'App name', 'App name', '')
        if dlg.ShowModal() == wx.ID_OK:
            p = dlg.GetValue().strip()
        dlg.Destroy()
        if p:
            from gluon.admin import app_create
            from gluon.globals import Request
            request = Request()
            request.folder = opj(self.w2p_path, 'applications', 'admin')
            ret = app_create(p, request)
            if not ret:
                wx.MessageDialog(self, 'Could not create app %s' % p, "error").ShowModal()
            else:
                self.panel.tree.rebuild_tree()

    def OnMenuAppOpen(self, evt):
        if not self.panel:
            self.AppOpen()
        else:
            self.panel.ClosePanel(self.ClosedPanel)
            self.AppOpen()

    def ClosedPanel(self, can_close):
        if can_close:
            self.server.process.Kill(self.server.pid)
            self.w2p_path = None
            self.panel.Destroy()
            self.panel = None
        #else:
        #    Flash(self)

    def OnMenuAppClose(self, evt):
        if self.panel:
            self.panel.ClosePanel(self.ClosedPanel)

    def OnMenuFileSave(self, evt):
        editor = self.panel.notebook.GetCurrentPage()
        if isinstance(editor, Editor):
            editor.savefile(editor.filename)

    def OnMenuFocusFileBrowser(self, evt):
        self.panel.tree.SetFocus()
        evt.Skip()

    def OnMenuFocusNotebook(self, evt):
        self.panel.notebook.SetFocus()
        evt.Skip()

    def OnMenuWindowsPrev(self, evt):
        self.panel.notebook.AdvanceSelection(False)
        evt.Skip()

    def OnMenuWindowsNext(self, evt):
        self.panel.notebook.AdvanceSelection(True)
        evt.Skip()

    def OnMenuCloseTab(self, evt):
        idx = self.panel.notebook.GetSelection()
        self.CloseTab(idx)
        evt.Skip()

    def OnMenuWindowClear(self, evt):
        ctrl = self.panel.log.notebook.GetCurrentPage()
        ctrl.ChangeValue('')
        evt.Skip()

    def CloseTab(self, idx):
        self.panel.notebook.DeletePage(idx)

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
            self.panel.rightwin.Show(not self.panel.rightwin.IsShown())
	    if IS_MAC:
		# Mac hack to force a relayout
		w, h = self.GetSize()
		self.SetSize((w-1, h-1))
		self.SetSize((w, h))
	    else:
                self.SendSizeEvent()
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

    #def OnMenuDebugEval(self, evt):
    #    if self.server and self.server.process is not None:
    #        dlg = wx.TextEntryDialog(self, 'arg to eval', 'arg', '')
    #        if dlg.ShowModal() == wx.ID_OK:
    #            val = dlg.GetValue().strip()
    #            if val:
    #                self.server.process.GetOutputStream().write("print %s\n" % val)

    def OnMenuDebugAddBP(self, evt):
        lineno = None
        dlg = wx.TextEntryDialog(self, 'Line number', 'Line Number', '')
        if dlg.ShowModal() == wx.ID_OK:
            lineno = int(dlg.GetValue())
        dlg.Destroy()
        if lineno:
            editor = self.panel.notebook.GetCurrentPage()
            filename = editor.filename
            if (str(lineno), filename) in self.panel.info.bp_list._bp_list:
                self.panel.info.bp_list.remove((str(lineno), filename))
                return
            editor.set_break(lineno, filename)
            self.panel.info.bp_list.append((str(lineno), filename))
            stream = self.server.process.GetOutputStream()
            stream.write('set_break %s %d\n' %(filename, lineno))

    def OnBPRemove(self, evt):
        lineno, filename = evt.GetMyVal()
        stream = self.server.process.GetOutputStream()
        stream.write('clear_break %s %s\n' %(filename, lineno))

        self.panel.open_tab(filename, get_dir_file(filename))
        editor = self.panel.notebook.GetCurrentPage()
        editor.clear_break(lineno)


    def from_debugger(self, text):
        command, text = text.split(':', 1)
        if command == 'STEP':
            self.TraceLine(text.strip())
        elif command == 'RES':
            lenght, text = text.split(':', 1)
            self.show_eval(text, lenght)
        elif command == "STOP":
            self.stop_debug()
        elif command == "START":
            self.sb.SetStatusText("serving")

    def shell_command(self, text):
        if self.server and self.server.process is not None:
            stream = self.server.process.GetOutputStream()
            stream.write('SH:%s\n' % text)

    def show_eval(self, text, lenght):
        missing = int(lenght)-len(text)
        if missing > 0:
            if self.server and self.server.process is not None:
                stream = self.server.process.GetInputStream()
                text += stream.read(missing)
        self.panel.log.shell_write(text)

    def OnTimer(self, evt=None):
        self.ToggleMenuDebugItems()
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
                self.panel.log.stderr_write(text)
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
                        self.panel.log.stdout_write(text)
                        return
                    if func == 'DBG':
                        self.from_debugger(text)
                    elif func == 'WSOUT':
                        what, lenght, text = text.split(':', 2)
                        missing = int(lenght)-len(text)
                        if missing > 0:
                            text += stream.read(missing)
                        if what == 'LOG':
                            self.panel.log.ws_write(text)
                        elif what == 'STATUS':
                            self.panel.log.stdout_write(text)
                        elif what == 'REQUEST_HEADERS':
                            self.panel.log.request_write(text)
                        elif what == 'RESPONSE_HEADERS':
                            self.panel.log.response_write(text)


    def AskPassword(self):
        p = None
        dlg = wx.TextEntryDialog(self, 'Admin Password', 'Admin Password', '')
        if dlg.ShowModal() == wx.ID_OK:
            p = dlg.GetValue()
        dlg.Destroy()
        return p

    def TraceLine(self, linetext):
        if self.previous_editor:
            self.previous_editor.trace_line_clear()

        filename, lineno, event = linetext.split('|')
        self.panel.open_tab(filename, get_dir_file(filename))

        editor = self.panel.notebook.GetCurrentPage()
        self.previous_editor = editor
        editor.trace_line(lineno)
        self.sb.SetStatusText("debugging")


    def stop_debug(self):
        if self.previous_editor:
            self.previous_editor.trace_line_clear()
        self.sb.SetStatusText("stop")


if __name__ == '__main__':
    w2p_path = None
    if len(sys.argv) > 1:
        if '-p' in sys.argv:
            idx = sys.argv.index('-p')
            try:
                PORT = int(sys.argv[idx+1])
            except ValueError:
                print "invalid port number"
                sys.exit(1)
            sys.argv.pop(idx+1)
            sys.argv.pop(idx)

        try:
            w2p_path = sys.argv[1]
        except IndexError:
            pass

    app = wx.App(False)
    f = Frame(None, size=(800, 600), w2p_path=w2p_path)
    f.SendSizeEvent()
    app.MainLoop()
