#!/usr/bin/env python
# coding: utf-8
import __builtin__

import wx
import wx.stc as stc
import wx.lib.mixins.listctrl as listmix
import wx.lib.flatnotebook as fnb
import wx.lib.newevent

(ShellEvent, EVT_SHELL) = wx.lib.newevent.NewCommandEvent()

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
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES)
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
        row, where = self.HitTest((evt.m_x, evt.m_y))

        if row > -1:
            tip = self._tooltips[row]
            self.SetToolTip(wx.ToolTip(tip))
        evt.Skip()

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        lineno = self.GetItemText(self.currentItem)
        filename = self.getColumnText(self.currentItem, 1)
        self.remove((lineno, filename))

    def OnGetItemText(self, item, col):
        return self._bp_list[item][col]

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def append(self, bp):
        self._bp_list.append(bp)
        self._tooltips.append(bp[1])
        self.SetItemCount(len(self._bp_list))

    def remove(self, bp):
        self._bp_list.remove(bp)
        self._tooltips.remove(bp[1])
        self.SetItemCount(len(self._bp_list))
        evt = MyEvent(myEVT_BPLIST_REMOVE, self.GetId())
        evt.SetMyVal(bp)
        self.GetEventHandler().ProcessEvent(evt)


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
            # FIXME: is this needed?
            while gtk.events_pending():
                gtk.main_iteration()
            wx.Panel.Refresh(self)

        def run_command(self, command_string):
            '''run_command runs the command_string in the terminal. This
            function will only return when self.thred_running is set to
            True, this is done by run_command_done_callback'''
            command = command_string.split(' ')
            pid = self.ctrl.fork_command(command=command[0],
                    argv=command, directory=os.getcwd())
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
            pid = self.run_command('vim -ni NONE %s -X -U NONE' % filename)
            os.chdir(current_path)
            return pid

        def savefile(self, filename):
            self.ctrl.feed_child(':w\n')

        def trace_line_clear(self):
            self.ctrl.feed_child(':match\n')

        def trace_line(self, lineno):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(":nnoremap <silent> <Leader>l ml:execute "
                                "'match Search /\%'.line('.').'l/'\n\l\n")

        def set_break(self, lineno, filename):
            self.ctrl.feed_child(':%s\nzo' % lineno)
            self.ctrl.feed_child(':sign define wholeline linehl=ErrorMsg\n')
            self.ctrl.feed_child(':sign place %d '
                    'name=wholeline line=%s file=%s\n' % (
                        lineno, lineno, filename))

        def clear_break(self, lineno):
            self.ctrl.feed_child(':sign unplace %s\n' % lineno)

else:
    FIXED_TABS = 0
    from editor import Editor


class TextCtrl(wx.TextCtrl):

    def __init__(self, parent,
           style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.TE_RICH2):
        wx.TextCtrl.__init__(self, parent, style=style)
        if not IS_MAC and not IS_WIN:
            self.SetBackgroundColour(wx.BLACK)
            self.SetForegroundColour(wx.WHITE)
            self.SetFont(wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False))


class ShellCtrl(TextCtrl):

    def __init__(self, parent):
        self._history = ['']
        self._hist_idx = 0
        self._prompt = '> '
        style = (wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH2 |
                wx.TE_PROCESS_ENTER)
        TextCtrl.__init__(self, parent, style)
        self.set_prompt()
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

    def set_prompt(self):
        TextCtrl.AppendText(self, self._prompt)

    def send_command(self, text):
        text = text.strip()
        if text:
            #self.GetTopLevelParent().shell_command(text)
            evt = ShellEvent(self.GetId(), text=text)
            #self.GetEventHandler().ProcessEvent(evt)
            wx.PostEvent(self, evt)

            self._history.append(text)
            self._hist_idx = len(self._history)
            if self._hist_idx > 1000:
                self._history.pop(1)
                self._hist_idx = len(self._history)
        else:
            wx.CallAfter(self.set_prompt)

    def Clear(self):
        TextCtrl.ChangeValue(self, '')
        self.set_prompt()

    def GetNumberOfLines(self):
        n = TextCtrl.GetNumberOfLines(self)
        if IS_MAC:
            return n - 1
        return n

    def GetCurrentLine(self):
        curPos = self.GetInsertionPoint()
        lineno = self.PositionToXY(curPos)[1]
        return lineno

    def GetLinePosition(self, lineno):
        x = self.GetLineLength(lineno)
        start = self.XYToPosition(0, lineno)
        end = start + x
        return (start, end)

    def ClearLine(self, lineno):
        start, end = self.GetLinePosition(lineno)
        #print start, end
        self.Replace(start, end, '')

    def OnKeyDown(self, evt):
        text = None
        key = evt.KeyCode
        if key == wx.WXK_DOWN:
            self._hist_idx += 1
            try:
                text = self._history[self._hist_idx]
            except IndexError:
                self._hist_idx = 0
                text = self._history[self._hist_idx]
        elif key == wx.WXK_UP:
            self._hist_idx -= 1
            try:
                text = self._history[self._hist_idx]
            except IndexError:
                self._hist_idx = len(self._history) - 1
                text = self._history[self._hist_idx]

        if text is not None:
            lineno = self.GetCurrentLine()
            self.ClearLine(lineno)
            self.set_prompt()
            TextCtrl.AppendText(self, text)
        else:
            evt.Skip()

    def OnEnter(self, evt):
        self.SetInsertionPointEnd()
        text = self.GetLineText(self.GetNumberOfLines()).lstrip(self._prompt)
        self.send_command(text.strip())
        evt.Skip()

    def AppendText(self, text):
        text = text.strip()
        if (text.startswith('<Storage {')
                or text.startswith('<Row {')
                or text.startswith('<DAL {')):
            text = text.split(', ')
            text = ',\n'.join(text)
        text = "%s\n" % text
        if IS_MAC:
            text = text.replace('\n', '\r')
        TextCtrl.AppendText(self, text)
        wx.CallAfter(self.set_prompt)


## Monkey patch: do not draw a focus rectangle on tabs
#NBRendererDefault_original = fnb.FNBRendererDefault
#class FNBRendererDefaultPatched(NBRendererDefault_original):
#    def DrawFocusRectangle(self, dc, pageContainer, page):
#        print 'aqui'
#        pass
#fnb.FNBRendererDefault = FNBRendererDefaultPatched


if IS_WIN:
    NotebookBase = wx.Notebook
else:

    class NB(fnb.FlatNotebook):

        def __init__(self, *args, **kwargs):
            fnb.FlatNotebook.__init__(self, *args, **kwargs)
            #self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_closing)

        #def on_closing(self, event):
        #    self.DeletePage(event.GetSelection())

        #def on_changed(self, event):
        #    wx.CallAfter(self.SetFocus)
        def AdvanceSelection(self, bForward=True):
            fnb.FlatNotebook.AdvanceSelection(self, bForward)
            self.SetFocus()


    NotebookBase = NB


class Notebook(NotebookBase):

    def __init__(self, parent, style):
        NotebookBase.__init__(self, parent, wx.ID_ANY, style=style)
        self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.OnSavePointLeft)
        self.Bind(stc.EVT_STC_SAVEPOINTREACHED, self.OnSavePointReached)

    def OnSavePointLeft(self, event):
        n = self.GetSelection()
        text = self.GetPageText(n)
        if text and text[0] != '*':
            text = '*%s' % text
            self.SetPageText(n, text)

    def OnSavePointReached(self, event):
        n = self.GetSelection()
        text = self.GetPageText(n)

        if text and text[0] == '*':
            self.SetPageText(n, text[1:])

#class Notebook(wx.Notebook):
#    def __init__(self, parent):
#        wx.Notebook.__init__(self, parent, style=wx.NB_MULTILINE)

    def GetChildren(self):
        return [c for c in NotebookBase.GetChildren(self) \
                if not isinstance(c, fnb.PageContainer)]

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
        #print idx
        #print ">>>", self.GetChildren()
        try:
            self.GetChildren()[idx].SetFocus()
        except IndexError:
            NotebookBase.SetFocus(self)

    def DeletePage(self, idx):
        #print idx
        if idx < 0:
            return

        w = self.GetPage(idx)
        if w and w.filename in ('<shell>',):
            return

        #wx.Notebook.DeletePage(self, idx)
        NotebookBase.DeletePage(self, idx)


class KeyValueList(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent,
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES | wx.LC_HRULES)

        self._data = []
        self.InsertColumn(0, "key")
        self.InsertColumn(1, "value")
        self.SetColumnWidth(0, 175)
        self.SetColumnWidth(1, 375)

    def OnGetItemText(self, item, col):
        data = self._data[item][col]
        return repr(data)[:300]

    def _getdata(self):
        return self._data

    def _setdata(self, data):
        self._data = data
        self.SetItemCount(len(data))

    def _deldata(self):
        self._data = []
        self.SetItemCount(0)
    data = property(_getdata, _setdata, _deldata)


class TreeDict(wx.TreeCtrl):

    def __init__(self, *args, **kwargs):
        wx.TreeCtrl.__init__(self, *args, **kwargs)
        self._dict = {}

    def append_dict(self, root, d):
        for key, value in d.iteritems():
            if not isinstance(key, basestring):
                key = repr(key)
            new_item = self.AppendItem(root, key)
            if isinstance(value, list):
                self.append_list(new_item, value)
            elif isinstance(value, dict):
                self.append_dict(new_item, value)
            elif isinstance(value, (basestring, int, long, float)):
                if isinstance(value, basestring):
                    self.AppendItem(new_item, value)
                else:
                    self.AppendItem(new_item, str(value))
            else:
                #self.append_list(new_item, dir(value))
                self.AppendItem(new_item, repr(value))

    def append_list(self, parent_item, values):
        for value in values:
            if isinstance(value, dict):
                self.append_dict(parent_item, value)
            elif isinstance(value, (basestring, int, long, float)):
                if isinstance(value, basestring):
                    self.AppendItem(parent_item, value)
                else:
                    self.AppendItem(parent_item, str(value))
            elif isinstance(value, list):
                self.append_list(parent_item, value)
            else:
                #self.append_list(parent_item, dir(value))
                self.AppendItem(parent_item, repr(value))

    def _getdata(self):
        return self._data

    def _setdata(self, data):
        if self._dict:
            self.DeleteAllItems()
        self._dict = dict(data)
        root = self.AddRoot("Items")
        self.append_dict(root, self._dict)
        self.Expand(root)

    def _deldata(self):
        self._dict = {}
        self.DeleteAllItems()
    data = property(_getdata, _setdata, _deldata)

