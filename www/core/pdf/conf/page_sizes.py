# -*- coding:Utf-8 -*-

from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, portrait, landscape


__all__ = (
    'mapping',
    'a4',
    'letter'
    'legal'
)


class PageSize(object):
    width = None
    height = None
    margin = (25*mm, 20*mm, 25*mm, 20*mm)  # top, right, bottom, left
    bending_pos = ((.5,), (.66, .32))  # 2-part, 3-part positions (percent)

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def portrait(self):
        return portrait(self.size)

    @property
    def landscape(self):
        return landscape(self.size)

    def available_width(self, used_width=0):
        return self.width - self.margin[1] - self.margin[3] - used_width

    def available_height(self, used_height=0):
        return self.height - self.margin[0] - self.margin[2] - used_height

    def from_left(self, used_width=0):
        return self.margin[1] + used_width

    def from_bottom(self, used_height=0):
        return self.height - self.margin[0] - used_height

    def scaled_width(self, dimension, base=A4, inner=True):
        if isinstance(dimension, (list, tuple)):
            return [self.scaled_width(dim, base, inner) for dim in dimension]
        else:
            if inner:
                return dimension * self.available_width() / (base[0] - self.margin[1] - self.margin[3])
            else:
                return dimension * self.width / base[0]

    def scaled_height(self, dimension, base=A4, inner=True):
        if isinstance(dimension, (list, tuple)):
            return [self.scaled_height(dim, base, inner) for dim in dimension]
        else:
            if inner:
                return dimension * self.available_height() / (base[1] - self.margin[0] - self.margin[2])
            else:
                return dimension * self.height / base[1]


# Page sizes
a4 = type('A4', (PageSize,), dict(width=A4[0], height=A4[1]))()
letter = type('Letter', (PageSize,), dict(width=LETTER[0], height=LETTER[1]))()
legal = type('Legal', (PageSize,), dict(width=LEGAL[0], height=LEGAL[1]))()


mapping = {
    'a4': a4,
    'letter': letter,
    'legal': legal
}
