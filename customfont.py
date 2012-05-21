import wx


# Adapted from http://wiki.wxpython.org/UsingFonts snippet
def _windows_load_font(filename):
    from ctypes import WinDLL
    gdi32 = WinDLL("gdi32.dll")
    gdi32.AddFontResourceA(filename)


plat = wx.PlatformInfo
if 'wxMSW' in plat:
    load_font = _windows_load_font
else:
    # dummy function
    load_font = lambda x: None
