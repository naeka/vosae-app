# -*- coding:Utf-8 -*-

from reportlab.lib.colors import Color, HexColor, transparent


def hsl(self):
    "Returns a three-tuple of components"
    _max = max(self.rgb())
    _min = min(self.rgb())
    if _max == _min:
        hue = 0
    elif _max == self.red:
        hue = (60 * ((self.green - self.blue)/(_max - _min))) % 360
    elif _max == self.green:
        hue = 120 + 60 * ((self.blue - self.red)/(_max - _min))
    elif _max == self.blue:
        hue = 240 + 60 * ((self.red - self.green)/(_max - _min))
    luminance = (_max + _min) / 2
    if _max == _min:
        saturation = 0
    elif luminance <= 0.5:
        saturation = (_max - _min) / (2 * luminance)
    elif luminance > 0.5:
        saturation = (_max - _min) / (2 - 2 * luminance)
    return (hue, saturation, luminance)


# Monkey patch Color
Color.hsl = hsl


font_color = HexColor('#333333')
white = HexColor('#FFFFFF')

orange = HexColor('#EB5F3A')
green = HexColor('#44B2AE')
yellow = HexColor('#F2DD93')
red = HexColor('#EB5F3A')
lightgrey = HexColor('#F5F5F5')
lightergrey = HexColor('#F7F7F7')
grey = HexColor('#EEEEEE')
darkgrey = HexColor('#DCDCDC')
darkergrey = HexColor('#CCCCCC')
