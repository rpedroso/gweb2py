# -*- coding: utf-8 -*-

import wx.stc as stc

def keywords():
    return (
        'ABORT ACTION ADD AFTER ALL ALTER ANALYZE AND AS ASC ATTACH'
        ' AUTOINCREMENT BEFORE BEGIN BETWEEN BY CASCADE CASE CAST CHECK'
        ' COLLATE COLUMN COMMIT CONFLICT CONSTRAINT CREATE CROSS'
        ' CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP DATABASE DEFAULT'
        ' DEFERRABLE DEFERRED DELETE DESC DETACH DISTINCT DROP EACH'
        ' ELSE END ESCAPE EXCEPT EXCLUSIVE EXISTS EXPLAIN FAIL FOR'
        ' FOREIGN FROM FULL GLOB GROUP HAVING IF IGNORE IMMEDIATE IN'
        ' INDEX INDEXED INITIALLY INNER INSERT INSTEAD INTERSECT INTO'
        ' IS ISNULL JOIN KEY LEFT LIKE LIMIT MATCH NATURAL NO NOT'
        ' NOTNULL NULL OF OFFSET ON OR ORDER OUTER PLAN PRAGMA'
        ' PRIMARY QUERY RAISE REFERENCES REGEXP REINDEX RELEASE'
        ' RENAME REPLACE RESTRICT RIGHT ROLLBACK ROW SAVEPOINT SELECT'
        ' SET TABLE TEMP TEMPORARY THEN TO TRANSACTION TRIGGER UNION'
        ' UNIQUE UPDATE USING VACUUM VALUES VIEW VIRTUAL WHEN WHERE')

def styles(faces):
    return {
    stc.STC_SQL_CHARACTER:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENT:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENTDOC:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENTDOCKEYWORD:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENTDOCKEYWORDERROR:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENTLINE:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_COMMENTLINEDOC:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_DEFAULT:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_IDENTIFIER:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_NUMBER:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_OPERATOR:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_QUOTEDIDENTIFIER:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_SQL_SQLPLUS:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_SQLPLUS_COMMENT:
        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_SQLPLUS_PROMPT:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_STRING:
        "fore:#bb5f5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_USER1:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_USER2:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_USER3:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_USER4:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_WORD:
        "fore:#009999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_SQL_WORD2:
        "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
}

def style_control(ctrl, faces, offset=0):
    set_style = ctrl.StyleSetSpec
    for key, value in styles(faces).iteritems():
        set_style(key + offset, value)

if __name__ == '__main__':
    import wx
    import wx.stc as stc
    styles = [a for a in dir(stc) if a.startswith('STC_SQL_')]
    for style in styles:
        print '    stc.%s:' % style
        if 'COMMENT' in style:
            print ('        "fore:#5fbb5f,back:%(back)s,face:%(helv)s,'
                    'size:%(size)d" % faces,')
        elif 'STRING' in style:
            print ('        "fore:#bb5f5f,back:%(back)s,face:%(helv)s,'
                    'size:%(size)d" % faces,')
        elif 'IDENTIFIER' in style:
            print ('        "fore:#999999,back:%(back)s,face:%(helv)s,'
                    'size:%(size)d,bold" % faces,')
        else:
            print ('        "fore:#999999,back:%(back)s,face:%(helv)s,'
                    'size:%(size)d" % faces,')


