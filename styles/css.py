# -*- coding: utf-8 -*-

import wx.stc as stc

def keywords():
    return ()

def styles(faces):
    return {
    stc.STC_CSS_DEFAULT:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_ATTRIBUTE:
     "fore:#0040c0,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_CLASS:
     "fore:#5f5fbb,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_COMMENT:
     "fore:#5fbb5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_DIRECTIVE:
     "fore:#5f5fbb,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_DOUBLESTRING:
     "fore:#bb5f5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_ID:
     "fore:#aa00aa,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_IDENTIFIER:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_IDENTIFIER2:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_IMPORTANT:
     "fore:#ffffff,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_OPERATOR:
     "fore:#777777,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_PSEUDOCLASS:
     "fore:#7f00bf,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_SINGLESTRING:
     "fore:#bb5f5f,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_TAG:
     "fore:#999f9f,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_UNKNOWN_IDENTIFIER:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_UNKNOWN_PSEUDOCLASS:
     "fore:#aa0000,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_VALUE:
        "fore:#ff00ff,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
}

def style_control(ctrl, faces, offset=0):
    set_style = ctrl.StyleSetSpec
    for key, value in styles(faces).iteritems():
        set_style(key + offset, value)
