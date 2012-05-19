# coding: utf-8

import keyword
import wx.stc as stc


def keywords():
    try:
        import gluon
        kw_gluon = gluon.__all__
    except ImportError:
        kw_gluon = ['A', 'B', 'BEAUTIFY', 'BODY', 'BR', 'CAT', 'CENTER',
                'CLEANUP', 'CODE', 'CRYPT', 'DAL', 'DIV', 'EM', 'EMBED',
                'FIELDSET', 'FORM', 'Field', 'H1', 'H2', 'H3', 'H4', 'H5',
                'H6', 'HEAD', 'HR', 'HTML', 'HTTP', 'I', 'IFRAME', 'IMG',
                'INPUT', 'IS_ALPHANUMERIC', 'IS_DATE', 'IS_DATETIME',
                'IS_DATETIME_IN_RANGE', 'IS_DATE_IN_RANGE',
                'IS_DECIMAL_IN_RANGE', 'IS_EMAIL', 'IS_EMPTY_OR',
                'IS_EQUAL_TO', 'IS_EXPR', 'IS_FLOAT_IN_RANGE', 'IS_IMAGE',
                'IS_INT_IN_RANGE', 'IS_IN_DB', 'IS_IN_SET', 'IS_IPV4',
                'IS_LENGTH', 'IS_LIST_OF', 'IS_LOWER', 'IS_MATCH',
                'IS_NOT_EMPTY', 'IS_NOT_IN_DB', 'IS_NULL_OR', 'IS_SLUG',
                'IS_STRONG', 'IS_TIME', 'IS_UPLOAD_FILENAME', 'IS_UPPER',
                'IS_URL', 'LABEL', 'LEGEND', 'LI', 'LINK', 'LOAD',
                'MARKMIN', 'MENU', 'META', 'OBJECT', 'OL', 'ON',
                'OPTGROUP', 'OPTION', 'P', 'PRE', 'SCRIPT', 'SELECT',
                'SPAN', 'SQLFORM', 'SQLTABLE', 'STYLE', 'TABLE', 'TAG',
                'TBODY', 'TD', 'TEXTAREA', 'TFOOT', 'TH', 'THEAD',
                'TITLE', 'TR', 'TT', 'UL', 'URL', 'XHTML', 'XML',
                'redirect', 'current', 'embed64',
                ]

    kw_gluon += [
            'request', 'response', 'session', 'cache', 'T',
            'db', 'auth', 'crud', 'mail', 'service', 'plugins',
            ]
    kw_gluon_tpl = ['extend', 'include', 'block', 'end',]

    kwlist = keyword.kwlist + kw_gluon + kw_gluon_tpl

    return " ".join(kwlist)


def styles(faces):
    # Python styles
    return {
        stc.STC_STYLE_DEFAULT: "back:#000000,fore:#999999",

        # Default
        stc.STC_P_DEFAULT:
        "back:#000000,fore:#999999,face:%(helv)s,size:%(size)d" % faces,
        # Comments
        stc.STC_P_COMMENTLINE:
        "back:#000000,fore:#007F00,face:%(other)s,size:%(size)d" % faces,
        # Number
        stc.STC_P_NUMBER:
        "back:#000000,fore:#007F7F,size:%(size)d" % faces,
        # String
        stc.STC_P_STRING:
        "back:#000000,fore:#7F007F,face:%(helv)s,size:%(size)d" % faces,
        # Single quoted string
        stc.STC_P_CHARACTER:
        "back:#000000,fore:#7F007F,face:%(helv)s,size:%(size)d" % faces,
        # Keyword
        stc.STC_P_WORD:
        "back:#000000,fore:#00007F,bold,size:%(size)d" % faces,
        # Triple quotes
        stc.STC_P_TRIPLE:
        "back:#000000,fore:#7F0000,size:%(size)d" % faces,
        # Triple double quotes
        stc.STC_P_TRIPLEDOUBLE:
        "back:#000000,fore:#7F0000,size:%(size)d" % faces,
        # Class name definition
        stc.STC_P_CLASSNAME:
        "back:#000000,fore:#0000FF,bold,underline,size:%(size)d" % faces,
        # Function or method name definition
        stc.STC_P_DEFNAME:
        "back:#000000,fore:#007F7F,bold,size:%(size)d" % faces,
        # Operators
        stc.STC_P_OPERATOR:
        "back:#000000,fore=999999,bold,size:%(size)d" % faces,
        # Identifiers
        stc.STC_P_IDENTIFIER:
        "back:#000000,fore:#999999,face:%(helv)s,size:%(size)d" % faces,
        # Comment-blocks
        stc.STC_P_COMMENTBLOCK:
        "back:#000000,fore:#7F7F7F,size:%(size)d" % faces,
        # End of line where string is not closed
        stc.STC_P_STRINGEOL:
        "back:#000000,fore:#999999,face:%(mono)s,eol,size:%(size)d" % faces,
           }


def style_control(ctrl, faces, offset=0):
    set_style = ctrl.StyleSetSpec
    for key, value in styles(faces).iteritems():
        set_style(key + offset, value)
    ctrl.StyleSetSpec(0, "back:#000000,fore:#999999")

