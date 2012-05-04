import sys
import wx
import wx.stc as stc
import keyword

faces = { 'times': 'Ubuntu Mono',
          'mono' : 'Ubuntu Mono',
          'helv' : 'Ubuntu Mono',
          'other': 'Ubuntu Mono',
          'size' : 10,
          'size2': 10,
         }

class PythonSTC(stc.StyledTextCtrl):

    fold_symbols = 2
    MARK_BP = 1
    MARK_LINE_BP = 2
    MARK_DEBUG = 3
    MARK_LINE_DEBUG = 4

    def __init__(self, parent, ID=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        #self.SetBufferedDraw(False)
        #self.SetViewEOL(True)
        #self.SetEOLMode(stc.STC_EOL_CRLF)
        self.SetUseAntiAliasing(True)

        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(79)

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

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)

        self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self. OnSavePointLeft)
        self.Bind(stc.EVT_STC_SAVEPOINTREACHED, self. OnSavePointReached)

        self._dirty = False

    def style_it(self):
        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#000000,back:#cdedff,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

    def python_styles(self):
        # Python styles
        # Default 
        self.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comments
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number
        self.StyleSetSpec(stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Single quoted string
        self.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Keyword
        self.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # Triple quotes
        self.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        # Triple double quotes
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        # Class name definition
        self.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # Function or method name definition
        self.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Operators
        self.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        # Identifiers
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comment-blocks
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        self.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

    def OnSavePointLeft(self, evt):
        self._dirty = True

    def OnSavePointReached(self, evt):
        self._dirty = False

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

class Editor(PythonSTC):
    def trace_line_clear(self):
        self.MarkerDeleteAll(PythonSTC.MARK_DEBUG)
        self.MarkerDeleteAll(PythonSTC.MARK_LINE_DEBUG)

    def trace_line(self, lineno):
        #self.ctrl.feed_child('^[:%s\nzo' % lineno)
        #self.ctrl.feed_child("^[:nnoremap <silent> <Leader>l ml:execute 'match Search /\%'.line('.').'l/'\n\l\n")
        lineno = int(lineno)
        lineno -=1
        self.MarkerAdd(lineno, PythonSTC.MARK_DEBUG)
        self.MarkerAdd(lineno, PythonSTC.MARK_LINE_DEBUG)
        self.GotoLine(lineno)
        self.Refresh(lineno)

    def set_break(self, lineno, filename):
        lineno = int(lineno)
        lineno -=1
        self.MarkerAdd(lineno, PythonSTC.MARK_BP)
        self.MarkerAdd(lineno, PythonSTC.MARK_LINE_BP)
        self.Refresh()
        #wx.CallAfter(self.MarkerAdd, 10, MARK_LINE_BP)
        #wx.CallAfter(self.MarkerAdd, 1, MARK_DEBUG)
        #wx.CallAfter(self.MarkerAdd, 1, MARK_LINE_DEBUG)
    def clear_break(self, lineno):
        lineno = int(lineno)
        lineno -=1
        self.MarkerDelete(lineno, PythonSTC.MARK_BP)
        self.MarkerDelete(lineno, PythonSTC.MARK_LINE_BP)
        self.Refresh()

    def run_command(self, *args):
        pass

    def quit(self):
        if self._dirty:
            return
        notebook = self.GetParent()
        page_n = notebook.get_selection_by_filename(self.filename)
        notebook.DeletePage(page_n)

    def openfile(self, filename):
        #print filename.endswith('.py')
        if filename.endswith('.py'):
            self.SetLexer(stc.STC_LEX_PYTHON)
            self.SetProperty("fold", "1")
            self.SetProperty("tab.timmy.whinge.level", "1")
            self.SetKeyWords(0, " ".join(keyword.kwlist))
            self.style_it()
            self.python_styles()
        else:
            self.SetLexer(stc.STC_LEX_HTML)
            self.SetProperty("asp.default.language", "1")
            self.SetProperty("fold", "1")

        self.SetIndent(4)               # Proscribed indent size for wx
        self.SetIndentationGuides(True) # Show indent guides
        self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self.SetTabIndents(True)        # Tab key indents
        self.SetTabWidth(4)             # Proscribed tab size for wx
        self.SetUseTabs(False)          # Use spaces rather than tabs, or
                                            # TabTimmy will complain!    
        f = open(filename)
        t = f.read()
        f.close()

        try:
            t = t.decode('utf-8')
        except UnicodeDecodeError:
            t = t.decode('latin-1')

        self.SetText(t)

        self.SetSavePoint()
        return 0

    def savefile(self, filename):
        #print >>sys.stderr, self.GetText()
        f = open(filename, 'wt')
        try:
            f.write(self.GetText())
        finally:
	    f.close()
        self.SetSavePoint()

if __name__ == '__main__':
    app = wx.App()
    f = wx.Frame(None)
    ed = Editor(f)

    ed.SetText(open('stc_test.py').read())
    ed.EmptyUndoBuffer()
    ed.Colourise(0, -1)

    # line numbers in the margin

    f.Show()
    ed.set_break(1, 'teste')
    f.Refresh()
    app.MainLoop()
