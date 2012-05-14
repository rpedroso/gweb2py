# -*- coding: utf-8 -*-

# Base on:
#
# #
# # Jan Thor
# # 2011-10-27T21:30:37Z      (UTC,
# # 2011-10-27T23:30:37+02:00 (Mitteleuropäische Sommerzeit,
# #
# 
# u"""
# TODO:
# """
# 
# __author__ = u"Jan Thor"
# __date__ = u"2011-10-27"
# __version__ = u"0.0.1"
# __credits__ = u"""http://www.janthor.com"""
# __docformat__ = u"restructuredtext de"

import wx.stc

HTML_KEYWORDS = ("a abbr acronym address applet area b base basefont bdo big"
    " blockquote body br button caption center cite code col colgroup dd del"
    " dfn dir div dl dt em fieldset font form frame frameset h1 h2 h3 h4 h5 h6"
    " head hr html i iframe img input ins isindex kbd label legend li link map"
    " menu meta noframes noscript object ol optgroup option p param pre q s"
    " samp script select small span strike strong style sub sup table tbody"
    " td textarea tfoot th thead title tr tt u ul var xml xmlns abbr"
    " accept-charset accept accesskey action align alink alt archive axis"
    " background bgcolor border cellpadding cellspacing char charoff charset"
    " checked cite class classid clear codebase codetype color cols colspan"
    " compact content coords data datafld dataformatas datapagesize datasrc"
    " datetime declare defer dir disabled enctype event face for frame"
    " frameborder headers height href hreflang hspace http-equiv id ismap"
    " label lang language leftmargin link longdesc marginwidth marginheight"
    " maxlength media method multiple name nohref noresize noshade nowrap"
    " object onblur onchange onclick ondblclick onfocus onkeydown onkeypress"
    " onkeyup onload onmousedown onmousemove onmouseover onmouseout onmouseup"
    " onreset onselect onsubmit onunload profile prompt readonly rel rev rows"
    " rowspan rules scheme scope selected shape size span src standby start"
    " style summary tabindex target text title topmargin type usemap valign"
    " value valuetype version vlink vspace width text password checkbox radio"
    " submit reset file hidden image article aside calendar canvas card"
    " command commandset datagrid datatree footer gauge header m menubar"
    " menulabel nav progress section switch tabbox active command"
    " contenteditable ping public !doctype")

def html_styles(faces):
    return {
    wx.stc.STC_H_DEFAULT:
        "fore:#000000,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_TAG:
        "fore:#000000,back:#ffffff,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_H_TAGUNKNOWN:
        "fore:#ff0000,back:#ffffff,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_H_ATTRIBUTE:
        "fore:#0040c0,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_ATTRIBUTEUNKNOWN:
        "fore:#ff0000,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_NUMBER:
        "fore:#cc0000,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_DOUBLESTRING:
        "fore:#7f00bf,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SINGLESTRING:
        "fore:#7f00bf,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_OTHER:
        "fore:#800080,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_COMMENT:
        "fore:#007f00,back:#eeffee,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_ENTITY:
        "fore:#336600,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_TAGEND:
        "fore:#000080,back:#ffffff,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_H_XMLSTART:
        "fore:#0000ff,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_XMLEND:
        "fore:#0000ff,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SCRIPT:
        "fore:#000080,back:#ffffff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_ASP:
        "fore:#000000,back:#ffff00,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_ASPAT:
        "fore:#000000,back:#ffdf00,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_CDATA:
        "fore:#000000,back:#ffdf00,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_QUESTION:
        "fore:#0000ff,back:#ffefbf,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_VALUE:
        "fore:#ff00ff,back:#ffefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_XCCOMMENT:
        "fore:#000000,back:#ffffd0,face:%(helv)s,size:%(size)d" % faces,

    wx.stc.STC_H_SGML_DEFAULT:
        "fore:#000080,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_COMMAND:
        "fore:#000080,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_1ST_PARAM:
        "fore:#006600,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_DOUBLESTRING:
        "fore:#800000,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_SIMPLESTRING:
        "fore:#993300,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_ERROR:
        "fore:#800000,back:#ff6666,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_SPECIAL:
        "fore:#3366ff,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_ENTITY:
        "fore:#333333,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_COMMENT:
        "fore:#808000,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_1ST_PARAM_COMMENT:
        "fore:#808000,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_H_SGML_BLOCK_DEFAULT:
        "fore:#000066,back:#CCCCE0,face:%(helv)s,size:%(size)d" % faces,

    wx.stc.STC_HPHP_DEFAULT:
        "fore:#000033,back:#efefff,face:%(helv)s,size:%(size)d,eolfilled" % faces,
    wx.stc.STC_HPHP_HSTRING:
        "fore:#bF00bF,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HPHP_SIMPLESTRING:
        "fore:#009F00,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HPHP_WORD:
        "fore:#7F007F,back:#efefff,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_HPHP_NUMBER:
        "fore:#CC9900,back:#efefff,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HPHP_VARIABLE:
        "fore:#00007F,back:#efefff,face:%(helv)s,size:%(size)d,italics" % faces,
    wx.stc.STC_HPHP_COMMENT:
        "fore:#3F7F3F,back:#efffff,face:%(helv)s,size:%(size)d,italics" % faces,
    wx.stc.STC_HPHP_COMMENTLINE:
        "fore:#007F00,back:#effffe,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HPHP_HSTRING_VARIABLE:
        "fore:#00007F,back:#efefff,face:%(helv)s,size:%(size)d,italics" % faces,
    wx.stc.STC_HPHP_OPERATOR:
        "fore:#660000,back:#efefff,face:%(helv)s,size:%(size)d" % faces,

    wx.stc.STC_HJ_START:
        "fore:#000033,back:#ffefef,face:%(helv)s,size:%(size)d,eolfilled" % faces,
    wx.stc.STC_HJ_DEFAULT:
        "fore:#7F7F00,back:#ffefef,face:%(helv)s,size:%(size)d,bold,eolfilled" % faces,
    wx.stc.STC_HJ_COMMENT:
        "fore:#3F7F3F,back:#ffffef,face:%(helv)s,size:%(size)d,italic" % faces,
    wx.stc.STC_HJ_COMMENTLINE:
        "fore:#007F00,back:#effffe,face:%(helv)s,size:%(size)d,italic" % faces,
    wx.stc.STC_HJ_COMMENTDOC:
        "fore:#330000,back:#ffdfdf,face:%(helv)s,size:%(size)d,italic" % faces,
    wx.stc.STC_HJ_NUMBER:
        "fore:#CC9900,back:#ffefef,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HJ_WORD:
        "fore:#000000,back:#ffefef,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HJ_KEYWORD:
        "fore:#00007f,back:#ffefef,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_HJ_DOUBLESTRING:
        "fore:#bF00bF,back:#ffefef,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HJ_SINGLESTRING:
        "fore:#009F00,back:#ffefef,face:%(helv)s,size:%(size)d" % faces,
    wx.stc.STC_HJ_SYMBOLS:
        "fore:#660000,back:#ffefef,face:%(helv)s,size:%(size)d,bold" % faces,
    wx.stc.STC_HJ_STRINGEOL:
        "fore:#BFBBB0,back:#ffefef,face:%(helv)s,size:%(size)d,eolfilled" % faces,
    wx.stc.STC_HJ_REGEX:
        "fore:#660033,back:#ffcfcf,face:%(helv)s,size:%(size)d" % faces,
}

def style_control(ctrl, faces):
    for key, value in html_styles(faces).iteritems():
        ctrl.StyleSetSpec(key, value)
