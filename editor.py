import sys
import wx
import wx.stc as stc
import keyword
import os

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Arial',
              'size' : 11,
              'size2': 9,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Monaco',
              'other': 'Monaco',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times New Roman',
              'mono' : 'Ubuntu Mono',
              'helv' : 'Ubuntu Mono',
              'other': 'Ubuntu Mono',
              'size' : 11,
              'size2': 9,
         }

class STC(stc.StyledTextCtrl):

    fold_symbols = 2
    MARK_BP = 1
    MARK_LINE_BP = 2
    MARK_DEBUG = 3
    MARK_LINE_DEBUG = 4

    def __init__(self, parent, ID=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.SetLayoutCache(wx.stc.STC_CACHE_DOCUMENT)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        self.SetBufferedDraw(True)
        #self.SetViewEOL(True)
        self.SetEOLMode(stc.STC_EOL_CR)
        self.SetUseAntiAliasing(True)

        #self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        #self.SetEdgeColumn(79)

        self.MarkerDefine(self.MARK_BP, stc.STC_MARK_CIRCLE, "red", "red")
        self.MarkerDefine(self.MARK_DEBUG, stc.STC_MARK_ARROW, "yellow", "yellow")
        self.MarkerDefine(self.MARK_LINE_BP, wx.stc.STC_MARK_BACKGROUND, 'white', 'red') 
        self.MarkerDefine(self.MARK_LINE_DEBUG, wx.stc.STC_MARK_BACKGROUND, 'white', 'yellow') 

        # debug margin
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        self.SetMarginSensitive(1, True)
        self.SetMarginWidth(1, 12)

        # line numbers in the margin
        self.SetMarginType(2, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(2, 25)

        # Setup a margin to hold fold markers
        self.SetMarginType(3, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(3, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(3, True)
        self.SetMarginWidth(3, 12)

        #wx.CallAfter(self.MarkerAdd, 10, MARK_BP)
        #wx.CallAfter(self.MarkerAdd, 10, MARK_LINE_BP)
        #wx.CallAfter(self.MarkerAdd, 1, MARK_DEBUG)
        #wx.CallAfter(self.MarkerAdd, 1, MARK_LINE_DEBUG)

        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_MINUS, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_PLUS,  "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

        self.SetCaretForeground("BLUE")

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)

        self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self. OnSavePointLeft)
        self.Bind(stc.EVT_STC_SAVEPOINTREACHED, self. OnSavePointReached)

        self._dirty = False

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                            "back:#000000,fore:#999999,"
                            "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        ## Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,
                "back:#C0C0C0,fore:#000000,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR,
                "back:#000000,fore:#cdedff,face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                "back:#000000,fore:#cdedff,face:%(other)s,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                "back:#000000,fore:#FF0000,face:%(other)s,bold")

    def OnSavePointLeft(self, evt):
        self._dirty = True
        evt.Skip()

    def OnSavePointReached(self, evt):
        self._dirty = False
        evt.Skip()

    def OnKeyDown(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.GetKeyCode()

        RETURN = (wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN)
        if key in RETURN and event.ControlDown():
            # Tips
            if event.ShiftDown():
                pos = self.GetCurrentPos()
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'lots of of text: blah, blah, blah\n\n'
                                 'show some suff, maybe parameters..\n\n'
                                 'fubar(param1, param2)')
            # Code completion
            else:
                #lst = []
                #for x in range(50000):
                #    lst.append('%05d' % x)
                #st = " ".join(lst)
                #print len(st)
                #self.AutoCompShow(0, st)

                kw = keyword.kwlist[:]
                #kw.append("this_is_a_much_much_much_much_much_much_much_longer_value")

                kw.sort()  # Python sorts are case sensitive
                self.AutoCompSetIgnoreCase(False)  # so this needs to match

                ## Images are specified with a appended "?type"
                #for i in range(len(kw)):
                #    if kw[i] in keyword.kwlist:
                #        kw[i] = kw[i] + "?1"

                self.AutoCompShow(0, " ".join(kw))

        elif key in RETURN:
            line = self.GetCurrentLine()
            text, _ = self.GetCurLine()
            pos = self.GetCurrentPos()
            c = self.GetCharAt(pos-1)
            print c
            last_indent = self.GetLineIndentation(line)
            if c and chr(c) in (':', '(', '{', '['):
                last_indent += 4
            elif 'return' in text:
                last_indent -= 4
            elif 'break' in text:
                last_indent -= 4
            elif 'pass' in text:
                last_indent -= 4

            self.NewLine()
            #self.SetLineIndentation(line+1, last_indent)
            self.AddText(' '*last_indent)
        else:
            event.Skip()

    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 3:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1

        return line

class Simple(STC):
    def setup(self):
        self.SetIndent(4)               # Proscribed indent size for wx
        self.SetIndentationGuides(False) # Show indent guides
        self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self.SetTabIndents(True)        # Tab key indents
        self.SetTabWidth(4)             # Proscribed tab size for wx
        self.SetUseTabs(False)          # Use spaces rather than tabs, or
                                        # TabTimmy will complain!    

class Python(STC):
    def setup(self):
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        from styles.py import style_control, keywords
        style_control(self, faces)

        self.SetKeyWords(0, keywords())

        self.SetIndent(4)               # Proscribed indent size for wx
        self.SetIndentationGuides(False) # Show indent guides
        self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self.SetTabIndents(True)        # Tab key indents
        self.SetTabWidth(4)             # Proscribed tab size for wx
        self.SetUseTabs(False)          # Use spaces rather than tabs, or
                                        # TabTimmy will complain!    

class HTML(STC):
    OFFSET_CURLY = 80 # ASP VBScript styles will be replaced with TeX styles
    TRIPLE_CURLY = chr(wx.stc.STC_P_TRIPLE + OFFSET_CURLY) * 4

    STATE_DEFAULT = 0
    STATE_CURLY = 1
    STATE_DELIM = 100

    STATE_TRANSITIONS = {
        STATE_DEFAULT: [("{{", STATE_CURLY, True)],
        STATE_CURLY: [("}}", STATE_DEFAULT, True)],
    }

    def setup(self):
        self.SetLexer(stc.STC_LEX_CONTAINER)
        self.SetStyleBits(7)
        self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.OnStyling)

        #self.SetProperty("asp.default.language", "1")
        #self.SetProperty("fold", "0")
        from styles.html import style_control, keywords
        from styles import py

        style_control(self, faces)
        py.style_control(self, faces, self.OFFSET_CURLY)

        # === Dummy controls as lexers ===
        self.dummyHtml = wx.stc.StyledTextCtrl(self)
        self.dummyHtml.SetLayoutCache(wx.stc.STC_CACHE_DOCUMENT)
        self.dummyHtml.Show(False)
        self.dummyHtml.SetLexer(wx.stc.STC_LEX_HTML)
        self.dummyHtml.SetKeyWords(0, keywords())

        self.dummyW2Pt = wx.stc.StyledTextCtrl(self)
        self.dummyW2Pt.SetLayoutCache(wx.stc.STC_CACHE_DOCUMENT)
        self.dummyW2Pt.Show(False)
        self.dummyW2Pt.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.dummyW2Pt.SetKeyWords(0, py.keywords())

    def _parse_html(self, fragment):
        self.dummyHtml.SetText(fragment.decode("utf-8"))
        fl = len(fragment)
        self.dummyHtml.Colourise(0, fl)
        multiplexed = self.dummyHtml.GetStyledText(0, fl)
        return multiplexed

    def _parse_w2pt(self, fragment, offset):
        self.dummyW2Pt.SetText(fragment.decode("utf-8"))
        fl = len(fragment)
        self.dummyW2Pt.Colourise(0, fl)
        multiplexed = self.dummyW2Pt.GetStyledText(0, fl)
        multiplexed = list(multiplexed)
        for i in range(1, len(multiplexed), 2):
            multiplexed[i] = chr(ord(multiplexed[i]) + offset)
        return "".join(multiplexed)

    def OnStyling(self, evt):
        u"""Called when the control needs styling."""
        text = self.GetText().encode("utf-8")

        # === split text into chunks ===
        splitpoints = [0]
        states = [self.STATE_DEFAULT]
        state = self.STATE_DEFAULT
        for i in range(0, len(text)):
            transitions = self.STATE_TRANSITIONS[state]
            for delim, newstate, bsplit in transitions:
                nd = len(delim)
                if i >= nd - 1 and text[i+1-nd:i+1] == delim:
                    if bsplit:
                        splitpoints.append(i-1)
                        splitpoints.append(i+1)
                        states.append(self.STATE_DELIM + state + newstate)
                        states.append(newstate)
                    state = newstate
        if splitpoints[-1] != len(text):
            splitpoints.append(len(text))
        parts = [text[splitpoints[i]:splitpoints[i+1]]
                 for i in range(len(splitpoints) - 1)]

        # === lex and style each part ===
        parsed = ""
        for i in range(len(parts)):
            type = states[i]
            fragment = parts[i]
            if type == self.STATE_DEFAULT:
                parsed += self._parse_html(fragment)
            elif type == self.STATE_CURLY:
                parsed += self._parse_w2pt(fragment, self.OFFSET_CURLY)
            elif type == self.STATE_CURLY + self.STATE_DELIM:
                parsed += self.TRIPLE_CURLY

        # === style the complete control ===
        self.StartStyling(0, 255)
        parsed = "".join([parsed[i] for i in range(1, len(parsed), 2)])
        self.SetStyleBytes(len(parsed), parsed)


class Editor(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

    def trace_line_clear(self):
        self._ctrl.MarkerDeleteAll(STC.MARK_DEBUG)
        self._ctrl.MarkerDeleteAll(STC.MARK_LINE_DEBUG)
        self._ctrl.Refresh()

    def trace_line(self, lineno):
        lineno = int(lineno)
        lineno -=1
        self._ctrl.MarkerAdd(lineno, STC.MARK_DEBUG)
        self._ctrl.MarkerAdd(lineno, STC.MARK_LINE_DEBUG)
        self._ctrl.GotoLine(lineno)
        self._ctrl.Refresh(lineno)

    def set_break(self, lineno, filename):
        lineno = int(lineno)
        lineno -=1
        self._ctrl.MarkerAdd(lineno, STC.MARK_BP)
        self._ctrl.MarkerAdd(lineno, STC.MARK_LINE_BP)
        self._ctrl.Refresh()

    def clear_break(self, lineno):
        lineno = int(lineno)
        lineno -=1
        self._ctrl.MarkerDelete(lineno, STC.MARK_BP)
        self._ctrl.MarkerDelete(lineno, STC.MARK_LINE_BP)
        self._ctrl.Refresh()

    def run_command(self, *args):
        pass

    def is_dirty(self):
        return self._ctrl._dirty

    def quit(self):
        if self._ctrl._dirty:
            return

        # FIXME: Send an Event
        notebook = self.GetParent()
        page_n = notebook.get_selection_by_filename(self.filename)
        #notebook.DeletePage(page_n)
        main_panel = self.GetParent().GetParent()
        main_panel.signal_can_close_tab(page_n)

    def openfile(self, filename, lineno=0):
        _, extension = os.path.splitext(filename)
        if extension == '.py':
            self._ctrl = Python(self)

        elif extension in ('.html', '.js'):
            self._ctrl = HTML(self)

        elif extension in ('.css'):
            self._ctrl = Simple(self)
            self._ctrl.SetLexer(stc.STC_LEX_CSS)
            self._ctrl.SetProperty("fold", "1")
            self._ctrl.SetProperty("tab.timmy.whinge.level", "1")
            from styles.css import style_control, keywords
            style_control(self._ctrl, faces)

        else:
            self._ctrl = Simple(self)

        self._sizer.Add(self._ctrl, 1, wx.EXPAND, 0)
        self._ctrl.setup()

        if lineno > 0:
            self.goto_line(lineno)

        self._ctrl.SetIndent(4)               # Proscribed indent size for wx
        self._ctrl.SetIndentationGuides(False) # Show indent guides
        self._ctrl.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self._ctrl.SetTabIndents(True)        # Tab key indents
        self._ctrl.SetTabWidth(4)             # Proscribed tab size for wx
        self._ctrl.SetUseTabs(False)          # Use spaces rather than tabs, or
                                            # TabTimmy will complain!    
        f = open(filename)
        t = f.read()
        f.close()

        try:
            t = t.decode('utf-8')
        except UnicodeDecodeError:
            t = t.decode('latin-1')

        self._ctrl.SetText(t)
        self._ctrl.EmptyUndoBuffer()
        wx.CallAfter(self._ctrl.SetSavePoint)

        self.Layout()

        return 0

    def savefile(self, filename):
        f = open(filename, 'wt')

        try:
            text = self._ctrl.GetText().encode('utf-8')
        except UnicodeDecodeError:
            text = self._ctrl.GetText().encode('latin-1')

        try:
            f.write(text)
        finally:
            f.close()

        self._ctrl.SetSavePoint()

    def goto_line(self, lineno):
        self._ctrl.GotoLine(lineno)


if __name__ == '__main__':
    app = wx.App()
    f = wx.Frame(None)
    sizer = wx.BoxSizer(wx.VERTICAL)
    ed = Editor(f)
    sizer.Add(ed, 1, wx.EXPAND, 0)
    f.SetSizer(sizer)

    ed.openfile(sys.argv[1])
    #ed._ctrl.EmptyUndoBuffer()
    #ed._ctrl.Colourise(0, -1)

    # line numbers in the margin

    f.Show()
    #ed.set_break(1, 'teste')
    #f.Refresh()
    app.MainLoop()
