# -*- coding: utf-8 -*-

import wx.stc as stc

def keywords():
    return ()

def styles(faces):
    return {
    stc.STC_CSS_DEFAULT:
     "fore:#99ff99,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_ATTRIBUTE:
     "fore:#0040c0,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_CLASS:
     "fore:#FF0080,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_COMMENT:
     "fore:#007f00,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_DIRECTIVE:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_DOUBLESTRING:
     "fore:#7f00bf,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_ID:
     "fore:#800080,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_IDENTIFIER:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_IDENTIFIER2:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_IMPORTANT:
     "fore:#ff0000,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_OPERATOR:
     "fore:#0f00bf,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_PSEUDOCLASS:
     "fore:#7f00bf,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_SINGLESTRING:
     "fore:#7f00bf,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_TAG:
     "fore:#999999,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_UNKNOWN_IDENTIFIER:
     "fore:#ff0000,back:%(back)s,face:%(helv)s,size:%(size)d,bold" % faces,
    stc.STC_CSS_UNKNOWN_PSEUDOCLASS:
     "fore:#ff0000,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
    stc.STC_CSS_VALUE:
        "fore:#ff00ff,back:%(back)s,face:%(helv)s,size:%(size)d" % faces,
}

def style_control(ctrl, faces, offset=0):
    set_style = ctrl.StyleSetSpec
    for key, value in styles(faces).iteritems():
        set_style(key + offset, value)
