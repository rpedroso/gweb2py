# -*- coding: utf-8 -*-
import wx.stc as stc

def keywords():
    return ("a abbr acronym address applet area b base basefont bdo big"
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

def styles(faces):
    return {
    stc.STC_H_DEFAULT:
     "fore:#999999,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_TAG:
     "fore:#336699,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_H_TAGUNKNOWN:
     "fore:#ff0000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_H_ATTRIBUTE:
     "fore:#0040c0,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_ATTRIBUTEUNKNOWN:
     "fore:#ff0000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_NUMBER:
     "fore:#cc0000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_DOUBLESTRING:
     "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SINGLESTRING:
     "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_OTHER:
     "fore:#800080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_COMMENT:
     "fore:#007f00,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_ENTITY:
     "fore:#336600,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_TAGEND:
     "fore:#000080,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_H_XMLSTART:
     "fore:#0000ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_XMLEND:
     "fore:#0000ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SCRIPT:
     "fore:#000080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_ASP:
     "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_ASPAT:
     "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_CDATA:
     "fore:#992222,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_QUESTION:
     "fore:#0000ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_VALUE:
     "fore:#ff00ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_XCCOMMENT:
     "fore:#007000,back:#000000,face:%(helv)s,size:%(size)d" % faces,

    stc.STC_H_SGML_DEFAULT:
     "fore:#000080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_COMMAND:
     "fore:#000080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_1ST_PARAM:
     "fore:#006600,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_DOUBLESTRING:
     "fore:#800000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_SIMPLESTRING:
     "fore:#993300,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_ERROR:
     "fore:#800000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_SPECIAL:
     "fore:#3366ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_ENTITY:
     "fore:#333333,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_COMMENT:
     "fore:#808000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_1ST_PARAM_COMMENT:
     "fore:#808000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_H_SGML_BLOCK_DEFAULT:
     "fore:#000066,back:#000000,face:%(helv)s,size:%(size)d" % faces,

    stc.STC_HJ_START:
     "fore:#000033,back:#000000,face:%(helv)s,size:%(size)d,eolfilled" % faces,
    stc.STC_HJ_DEFAULT:
     "fore:#7F7F00,back:#000000,face:%(helv)s,size:%(size)d,bold,eolfilled" % faces,
    stc.STC_HJ_COMMENT:
     "fore:#3F7F3F,back:#000000,face:%(helv)s,size:%(size)d,italic" % faces,
    stc.STC_HJ_COMMENTLINE:
     "fore:#007F00,back:#000000,face:%(helv)s,size:%(size)d,italic" % faces,
    stc.STC_HJ_COMMENTDOC:
     "fore:#330000,back:#000000,face:%(helv)s,size:%(size)d,italic" % faces,
    stc.STC_HJ_NUMBER:
     "fore:#CC9900,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_HJ_WORD:
     "fore:#999999,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_HJ_KEYWORD:
     "fore:#00007f,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_HJ_DOUBLESTRING:
     "fore:#bF00bF,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_HJ_SINGLESTRING:
     "fore:#009F00,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_HJ_SYMBOLS:
     "fore:#660000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_HJ_STRINGEOL:
     "fore:#BFBBB0,back:#000000,face:%(helv)s,size:%(size)d,eolfilled" % faces,
    stc.STC_HJ_REGEX:
     "fore:#660033,back:#000000,face:%(helv)s,size:%(size)d" % faces,

    #wx.stc.STC_CSS_ATTRIBUTE:
    #    "fore:#0040c0,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_CLASS:
    #    "fore:#000080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_COMMENT:
    #    "fore:#007f00,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_DEFAULT:
    #    "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_DIRECTIVE:
    #    "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_DOUBLESTRING:
    #    "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_ID:
    #    "fore:#800080,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_IDENTIFIER:
    #    "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    #wx.stc.STC_CSS_IDENTIFIER2:
    #    "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    #wx.stc.STC_CSS_IMPORTANT:
    #    "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_OPERATOR:
    #    "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_PSEUDOCLASS:
    #    "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_SINGLESTRING:
    #    "fore:#7f00bf,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_TAG:
    #    "fore:#000000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    #wx.stc.STC_CSS_UNKNOWN_IDENTIFIER:
    #    "fore:#ff0000,back:#000000,face:%(helv)s,size:%(size)d,bold" % faces,
    #wx.stc.STC_CSS_UNKNOWN_PSEUDOCLASS:
    #    "fore:#ff0000,back:#000000,face:%(helv)s,size:%(size)d" % faces,
    #wx.stc.STC_CSS_VALUE:
    #    "fore:#ff00ff,back:#000000,face:%(helv)s,size:%(size)d" % faces,
}

def style_control(ctrl, faces, offset=0):
    set_style = ctrl.StyleSetSpec
    for key, value in styles(faces).iteritems():
        set_style(key + offset, value)
