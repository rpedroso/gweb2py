import os
import wx
import wx.lib.mixins.listctrl as listmix


def parse_traceback(tb_str):
    lines = tb_str.splitlines()
    #print lines
    # filename, line, function, code
    _ = lines.pop(0)
    i = 0
    tb = []
    for n, line in enumerate(lines[:-1:2]):
        filename, lineno, function = map(lambda x: x.strip(), line.split(','))
        code = lines[n+1+i] #(n+2)*2]
        i += 1

        d = {}
        d['file'] = filename[6:-1]
        d['lnum'] = lineno[5:]
        d['func'] = function[3:]
        d['lines'] = {d['lnum']: code}
        tb.append(d)

    return tb


class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


# Copied and adapt from wxPython demo Main.py

class Error:
    """Wraps and stores information about the current exception"""

    def __init__(self, exc_info):
        try:
            excType = exc_info['snapshot']['etype']
            excValue = exc_info['snapshot']['evalue']
        except KeyError:
            excType = exc_info['output']
            excValue = exc_info['traceback'].splitlines()[-1]

        # traceback list entries: (filename, line number, function name, code)
        try:
            self.traceback = exc_info['snapshot']['frames']
        except KeyError:
            #print exc_info['traceback']
            self.traceback = parse_traceback(exc_info['traceback'])

        self.exception_type = excType

        ## If it's a syntax error, extra information needs
        ## to be added to the traceback
        #if excType is SyntaxError:
        #    try:
        #        msg, (filename, lineno, self.offset, line) = excValue
        #    except:
        #        pass
        #    else:
        #        if not filename:
        #            filename = "<string>"
        #        line = line.strip()
        #        self.traceback.append((filename, lineno, "", line))
        #        excValue = msg
        #try:
        #    self.exception_details = str(excValue)
        #except:
        #    self.exception_details = ("<unprintable %s object>" %
        #            type(excValue).__name__)
        self.exception_details = excValue

class ErrorPanel(wx.Panel):

    def __init__(self, parent, codePanel):
        wx.Panel.__init__(self, parent)
        self.codePanel = codePanel
        self.nb = parent

        self.box = wx.BoxSizer(wx.VERTICAL)

        # controls
        st_type = wx.StaticText(self, label="Type:")
        st_details = wx.StaticText(self, label="Details:")
        st_info = wx.StaticText(self, label=("Lines shown in blue: "
                    "Double-click on them to go to the offending line"))
        font = st_info.GetFont()
        font.SetPointSize(8)
        font.SetStyle(wx.FONTSTYLE_ITALIC)
        st_info.SetFont(font)

        self.error_list = ListCtrl(self, wx.ID_ANY,
                style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.st_type = st_type
        self.st_details = st_details

        self.error_list.InsertColumn(0, "Filename")
        self.error_list.InsertColumn(1, "Line", wx.LIST_FORMAT_RIGHT)
        self.error_list.InsertColumn(2, "Function")
        self.error_list.InsertColumn(3, "Code")
        #self.error_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        #self.error_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        self.box.Add(st_type, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        self.box.Add(st_details, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        self.box.Add(self.error_list, 1, wx.EXPAND | wx.ALL, 10)
        self.box.Add(st_info, 0, wx.ALIGN_LEFT | wx.ALL, 10)

        self.box.Fit(self)
        self.SetSizer(self.box)

        self.error_list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.error_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def set_error(self, error):
        self.__error = error
        self.st_type.SetLabel("Type: %s" % error.exception_type)
        self.st_details.SetLabel("Details: %s" % error.exception_details)
        self.__insert_traceback(self.error_list, error.traceback)

    def __insert_traceback(self, error_list, traceback):
        #Add the traceback data
        error_list.DeleteAllItems()
        for x in range(len(traceback)):
            data = traceback[x]
            error_list.InsertStringItem(x, os.path.basename(data['file'])) # Filename
            error_list.SetStringItem(x, 1, str(data['lnum']))              # Line
            error_list.SetStringItem(x, 2, str(data['func']))              # Function
            try:
                error_list.SetStringItem(x, 3, str(data['lines'][data['lnum']]).strip()) # Code
            except Exception, e:
                error_list.SetStringItem(x, 3, '')

            # Check whether this entry is from application code
            if 'applications' in data['file']:
                # Store line number for easy access
                self.error_list.SetItemData(x, int(data['lnum']))
                # Give it a blue colour
                item = self.error_list.GetItem(x)
                item.SetTextColour(wx.BLUE)
                self.error_list.SetItem(item)
            else:
                # Editor can't jump into this one's code
                self.error_list.SetItemData(x, -1)

    def OnItemSelected(self, event):
        # This occurs before OnDoubleClick and can be used to set the
        # currentItem. OnDoubleClick doesn't get a wxListEvent....
        self.currentItem = event.m_itemIndex
        event.Skip()

    def OnDoubleClick(self, event):
        # If double-clicking on a demo's entry, jump to the line number
        line = self.error_list.GetItemData(self.currentItem)
        if line != -1:
            #print line, self.__demo_error.traceback[self.currentItem]['file']
            filename = self.__error.traceback[self.currentItem]['file']
            #print filename
            wx.CallAfter(self.codePanel.JumpToLine, line, filename)
        event.Skip()


if __name__ == '__main__':
    app = wx.App(False)
    f = wx.Frame(None)
    import sys
    sys.path.insert(0, '/home/rpedroso/Projects/sandbox/web2py')
    import cPickle
    fi = open(('/home/rpedroso/Projects/sandbox/web2py/applications/minimal'
        '/errors/'
        '127.0.0.1.2012-05-14.20-49-29.6690b316-daa6-47fd-82a0-c640653158af'),
        'rb')
    error = Error(cPickle.load(fi))
    demoPage = ErrorPanel(f, None)
    demoPage.set_error(error)
    f.Show()
    app.MainLoop()
