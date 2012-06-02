#!/usr/bin/python

import wx
_ = wx.GetTranslation

import wx.grid as grid
import wx.stc as stc
import wx.lib.newevent

import os
import time

from editor import STC
from styles.sql import style_control, keywords

(SQLEvent, EVT_SQL) = wx.lib.newevent.NewCommandEvent()

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Ubuntu Mono',
              'mono' : 'Ubuntu Mono',
              'helv' : 'Ubuntu Mono',
              'other': 'Ubuntu Mono',
              'size' : 10,
              'size2': 10,
              # On Windows StyleTextCtrl cannot be "full" blackto avoid
              # the pointerto "disappear" until find a better solution
              'back': "#292929",
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Monaco',
              'other': 'Monaco',
              'size' : 12,
              'size2': 12,
              'back': "#000000",
             }
else:
    faces = { 'times': 'Times New Roman',
              'mono' : 'Ubuntu Mono',
              'helv' : 'Ubuntu Mono',
              'other': 'Ubuntu Mono',
              'size' : 10,
              'size2': 10,
              'back': "#000000",
         }


class SQL(STC):
    def OnKeyDown(self, event):
        event.Skip()

    def setup(self):
        self._auto_comp_keywords = keywords().lower()

        self.SetLexer(stc.STC_LEX_SQL)
        self.SetProperty("fold", "1")
        self.SetKeyWords(0, self._auto_comp_keywords)
        style_control(self, faces)

        self.AutoCompSetDropRestOfWord(False)
        self.AutoCompSetIgnoreCase(False)
        self.AutoCompSetChooseSingle(False)
        self.Bind(wx.EVT_KEY_UP, self.__on_key_up)

    def append_autocomp_keywords(self, kws):
        kws = ' '.join(kws).lower()
        self._auto_comp_keywords += ' %s' % kws

    def __on_key_up(self, event):
        if self.CallTipActive():
            self.CallTipCancel()

        key = event.GetKeyCode()
        RETURN = (wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN)

        if key == ord('('):
            self._show_code_tips(self.GetCurrentPos())
        elif key in RETURN and event.ControlDown():
            evt = SQLEvent(self.GetId())
            wx.PostEvent(self, evt)
        elif key in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT):
            pass
        elif (key < 255 and chr(key).isalpha()) or wx.WXK_BACK:
            self._show_code_completation(self.GetCurrentPos())
        event.Skip()

    def _show_code_tips(self, pos):
        pass

    def _show_code_completation(self, pos):
        text = self.GetText().encode("utf-8")
        s = self.WordStartPosition(pos, 1)
        e = self.WordEndPosition(pos, 1)
        word = self.GetTextRange(s, e)
        if not word:
            return

        kws = [kw for kw in self._auto_comp_keywords.split()
                if kw.startswith(word)]
        len_kws = len(kws)
        if len_kws < 1:
            return
        if len_kws == 1 and kws[0] == word:
            return

        lst = ' '.join(sorted(kws))
        if not self.AutoCompActive():
            self.AutoCompShow(pos - self.WordStartPosition(pos, True), lst)


class DataGrid(grid.Grid):
    def __init__(self, parent):
        grid.Grid.__init__(self, parent)
        self.moveTo = None
        self.EnableEditing(False)
        self.CreateGrid(0, 0)

        self.Bind(grid.EVT_GRID_LABEL_LEFT_DCLICK,
                self.__on_label_left_dclick)

    def __on_label_left_dclick(self, event):
        self.AutoSizeColumns()

    def clear_all(self):
        self.DeleteRows(pos=0, numRows=self.GetNumberRows(), updateLabels=True)
        self.DeleteCols(pos=0, numCols=self.GetNumberCols(), updateLabels=True)

    def set_data(self, header, data):
        self.clear_all()
        self.AppendCols(len(header))

        # set the header
        [self.SetColLabelValue(idx, each[0])
                for idx, each in enumerate(header)]

        # set Data
        rownum = -1
        self.AppendRows(len(data))
        for rownum, row in enumerate(data):
            [self.SetCellValue(rownum, idx, u'%s' % each)
                    for idx, each in enumerate(row)]

        return _("Records Retrived: %d") % (rownum+1)

class DBTree(wx.TreeCtrl):
    def __init__(self, *args, **kwargs):
        wx.TreeCtrl.__init__(self, *args, **kwargs)

        self._itemtext = None
        self.Bind(wx.EVT_MOTION, self.__on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)

    def __on_left_down(self, event):
        self._itemtext = None
        fields_text = None
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)
        if item:
            item_text = self.GetItemText(item)
            if item_text == 'Columns':
                (child, cookie) = self.GetFirstChild(item)

                fields = []
                while child:
                    fields.append(self.GetItemText(child).split(':', 1)[0])
                    (child, cookie) = self.GetNextChild(item, cookie)

                fields_text = ', '.join(fields)

            item_par = self.GetItemParent(item)
            if item_par:
                item_par_text = self.GetItemText(item_par)
                if item_par_text == 'table':
                    self._itemtext = ("select * from %s limit 100\n" %
                            item_text)
                elif fields_text:
                    self._itemtext = "select %s from %s limit 100\n" % (
                            fields_text, item_par_text)
        event.Skip()

    def __on_motion(self, event):
        if event.Dragging() and self._itemtext:
            data = wx.TextDataObject()
            data.SetText(self._itemtext)
            dropSource = wx.DropSource(self)
            dropSource.SetData(data)

            result = dropSource.DoDragDrop(True)
            self._itemtext = None

        event.Skip()

    def build(self, objects, parent):
        if isinstance(objects, list):
            for subobj in objects:
                self.AppendItem(parent, str(subobj))
                self.SetPyData(parent, None)
            return

        elif isinstance(objects, dict):
            obj_keys = objects.keys()
            obj_keys.sort()
            for subobj in obj_keys:
                child = self.AppendItem(parent, str(subobj))
                self.SetPyData(parent, None)
                self.build(objects[subobj], child)


class Viewer(wx.Panel):
    def __init__(self, parent, log, filename=None):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.log = log

        self.db = None
        self.filename = filename

        tree = DBTree(self, size=(200,-1))

        sqltext = SQL(self)
        sqltext.setup()

        execute_query = wx.Button(self, label="Execute query")

        grid = DataGrid(self)

        #info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        #font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        #info.SetFont(font)

        #grid.Hide()

        self.tree = tree
        self.grid = grid
        #self.info = info
        self.sqltext = sqltext
        self.execute_query = execute_query

        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        vert_sizer.Add(sqltext, 0, wx.EXPAND, 0)
        vert_sizer.Add(execute_query, 0, 0, 0)
        vert_sizer.Add(grid, 1, wx.EXPAND, 0)
        #vert_sizer.Add(info, 1, wx.EXPAND, 0)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(tree, 0, wx.EXPAND, 0)
        main_sizer.Add(vert_sizer, 1, wx.EXPAND, 0)

        self.SetSizer(main_sizer)
        self.Layout()

        execute_query.Bind(wx.EVT_BUTTON, self.on_execute_query)
        sqltext.Bind(EVT_SQL, self.on_execute_query)

        if filename is not None:
            self.attach_db(filename)

    def attach_db(self, filename):
        from gluon import DAL
        self.db = db = DAL('sqlite://%s' % filename, migrate=False)

        root = self.tree.AddRoot(os.path.basename(filename))
        objects = self._get_db_objects()
        self.tree.build(objects, root)
        self.sqltext.append_autocomp_keywords(self._tables)

        self.write_info("Write a SQL query and hit 'Execute query'.\n")

    def on_execute_query(self, event):
        start, end = self.sqltext.GetSelection()
        sqltext = self.sqltext.GetTextRange(start, end).strip()
        if not sqltext:
            sqltext = self.sqltext.GetText().strip()

        if not sqltext:
            return

        db = self.db
        try:
            rows = db.executesql(sqltext)
            #if not rows:
            #    self.write_info('%s\n' % sqltext)
            #    #self.show_grid(False)
            #    #return
            headers = db._adapter.cursor.description
            self.grid.set_data(headers, rows)
            self.write_info('%s\n' % sqltext)
        except Exception, e:
            self.write_info("%s\n" % repr(e.message))
            return

        self.grid.Refresh()
        #self.show_grid(True)

        wx.CallAfter(self.sqltext.SetFocus)

    def write_info(self, text):
        t = time.ctime()
        #self.info.AppendText('%s: %s\n' % (t, text))
        s = '%s: %s' % (t, text)
        self.log.log_append_text('stdout', s)

    def show_grid(self, show=True):
        #self.info.Show(not show)
        #self.grid.Show(show)
        self.Layout()

    def _get_db_objects(self):
        rows = self.db.executesql("""
            select type,name
            from sqlite_master
            where type in ('table','view') and name not like 'sqlite_%'
            order by type, name
            """)
        schema = {}

        self._tables = []
        for row in rows:
            db_type, db_name = row
            self._tables.append(db_name)
            if not schema.has_key(db_type):
                schema[db_type] = {db_name:None}
            tv_obj = schema[db_type]
            #Get Column Details
            tv_obj.update({db_name:{'Columns':self._getcolumns(db_name)}})
            #Get index Details
            if row[0] == 'table':
                index = self._getindexes(db_name)
                if index: tv_obj.get(db_name).update({'Indexes':index})
            schema[db_type].update(tv_obj)
        return schema

    def _getcolumns(self, dboject):
        rows = self.db.executesql("pragma table_info('%s')" % (dboject))
        cols = []
        for each in rows:
            (col_id, col_name, col_type, col_null, col_def, col_pk) = each

            if col_null == 0:
                 col_null = ' Null'
            else:
                 col_null = ' Not Null'

            if col_def is None:
                col_def = ''
            else:
                col_def = " Default '" + col_def + "'"

            col_name = col_name +':' +col_type + col_null+col_def
            cols.append(col_name)
        return cols

    def _getindexes(self, dboject):
        rows = self.db.executesql("""select name from sqlite_master where
        type='index' and tbl_name ='%s'""" % (dboject))
        objs = []
        for each in rows:
            idx_keys = each[0] + '('+self._getindexkeys(each[0]) +')'
            objs.append(idx_keys)
        return objs

    def _getindexkeys(self, dboject):
        rows = self.db.executesql("pragma index_info('%s')" % (dboject))
        objs = []
        for each in rows:
            objs.append(each[2])
        return ','.join(objs)

if __name__ == '__main__':
    def log(where, t):
        print t
    import sys
    sys.path.insert(0, '/home/rpedroso/Projects/sandbox/web2py')
    app = wx.App(0)
    f = wx.Frame(None, size=(600,400))
    f.log_append_text = log
    filename = '/home/rpedroso/Projects/sandbox/web2py/applications/store/databases/minhaloja.sqlite'
    p = Viewer(f, f, filename=filename)
    f.Show()
    app.MainLoop()
