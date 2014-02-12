# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext as _
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm, cm
from reportlab.lib import colors as base_colors
from reportlab.platypus import (
    Spacer,
    Frame,
    PageTemplate,
    PageBreak,
    CondPageBreak,
    KeepTogether,
    Table,
    TableStyle
)
from reportlab.platypus.flowables import HRFlowable

from core.pdf.conf import colors
from core.pdf.conf.fonts import get_font
from core.pdf.utils import (
    Paragraph,
    ReportingDocTemplate
)


__all__ = (
    'BaseTableStyle',
    'NoSplitFrame',
    'Report'
)


class BaseTableStyle(TableStyle):

    def __init__(self, name, cmds=None, parent=None, **kw):
        self.name = name
        TableStyle.__init__(self, cmds, parent, **kw)


class NoSplitFrame(Frame):

    def split(self, flowable, canv):
        splitted = Frame.split(self, flowable, canv)
        try:
            return [splitted[0]]
        except:
            return splitted


class Report(object):

    def __init__(self, report_settings, *args, **kwargs):
        self.settings = report_settings
        kwargs.update(
            pagesize=self.settings.page_size.portrait,
            leftMargin=self.settings.page_size.margin[3],
            rightMargin=self.settings.page_size.margin[1],
            topMargin=self.settings.page_size.margin[0],
            bottomMargin=self.settings.page_size.margin[2]
        )
        self.doc = ReportingDocTemplate(*args, **kwargs)
        self.story = []

    def init_report(self):
        self.generate_templates()
        self.generate_style()

    def fill(self):
        pass

    def set_metadata(self):
        pass

    def generate_templates(self):
        frame_kwargs = {
            # 'showBoundary': 1,  # For DEBUG purpose
            'leftPadding': 0,
            'rightPadding': 0,
            'topPadding': 0,
            'bottomPadding': 0
        }
        full_frame = Frame(
            self.settings.page_size.margin[3],
            self.settings.page_size.margin[2],
            self.settings.page_size.available_width(),
            self.settings.page_size.available_height(),
            **frame_kwargs
        )

        self.doc.addPageTemplates([
            PageTemplate(id='Everyone', frames=[full_frame], onPage=self.on_page_cb),
        ])

    def generate_style(self):
        self.style = StyleSheet1()

        self.style.add(ParagraphStyle(
            name='Normal',
            fontName=get_font(self.settings.font_name).regular,
            fontSize=self.settings.font_size,
            textColor=self.settings.hex_font_color,
            leading=1.2 * self.settings.font_size
        ), alias='p')

        self.style.add(ParagraphStyle(
            name='BodyText',
            parent=self.style['Normal'],
            spaceBefore=6
        ))

        self.style.add(ParagraphStyle(
            name='Italic',
            parent=self.style['BodyText'],
            fontName=get_font(self.settings.font_name).italic
        ))

        self.style.add(ParagraphStyle(
            name='Bold',
            parent=self.style['BodyText'],
            fontName=get_font(self.settings.font_name).bold
        ))

        self.style.add(ParagraphStyle(
            name='Heading1',
            parent=self.style['Normal'],
            fontName=get_font(self.settings.font_name).bold,
            fontSize=1.5 * self.settings.font_size,
            leading=2 * self.settings.font_size,
            spaceAfter=6
        ), alias='h1')

        self.style.add(ParagraphStyle(
            name='Heading2',
            parent=self.style['Normal'],
            fontName=get_font(self.settings.font_name).bold,
            fontSize=1.25 * self.settings.font_size,
            leading=1.75 * self.settings.font_size,
            spaceBefore=12,
            spaceAfter=6
        ), alias='h2')

        self.style.add(ParagraphStyle(
            name='Small',
            parent=self.style['Normal'],
            fontSize=0.9 * self.settings.font_size,
            leading=1 * self.settings.font_size,
        ))

        self.style.add(ParagraphStyle(
            name='Smaller',
            parent=self.style['Normal'],
            fontSize=0.75 * self.settings.font_size,
            leading=0.9 * self.settings.font_size,
        ))

        self.style.add(ParagraphStyle(
            name='PageNumbering',
            parent=self.style['Smaller'],
            alignment=TA_RIGHT
        ))

        self.style.add(BaseTableStyle(
            name='Table',
            cmds=[
                ('FONTNAME', (0, 0), (-1, -1), get_font(self.settings.font_name).regular),
                ('FONTSIZE', (0, 0), (-1, -1), self.settings.font_size),
                ('LEADING', (0, 0), (-1, -1), 1.2 * self.settings.font_size),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.settings.hex_font_color),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
        ))

        self.style.add(BaseTableStyle(
            name='LayoutTable',
            parent=self.style['Table'],
            cmds=[
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]
        ))

        self.style.add(BaseTableStyle(
            name='ReportTable',
            parent=self.style['Table'],
            cmds=[
                ('FONTNAME', (0, 0), (-1, 0), get_font(self.settings.font_name).bold),
                ('FONTSIZE', (0, 0), (-1, 0), 1.1 * self.settings.font_size),
                ('LEADING', (0, 0), (-1, 0), 1.4 * self.settings.font_size),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), (colors.transparent, self.settings.hex_base_color.clone(alpha=0.1))),
            ]
        ))

        # For monetary lists
        self.style.add(ParagraphStyle(
            name='Monospaced',
            parent=self.style['Normal'],
            fontName='Courier',  # MUST change to a font closest to the base one
        ))

    def on_page_cb(self, canvas, document):
        self.draw_bending_lines(canvas, document)
        self.header(canvas, document)
        self.footer(canvas, document)

    def on_first_page_cb(self, canvas, document):
        self.on_page_cb(canvas, document)

    def on_other_pages_cb(self, canvas, document):
        self.on_page_cb(canvas, document)

    def draw_bending_lines(self, canvas, document):
        # Bending lines
        canvas.saveState()
        canvas.setLineWidth(0.2)
        canvas.setLineCap(1)
        canvas.setStrokeColor(colors.darkergrey)
        height = self.settings.page_size.height
        # 2-part
        if self.settings.page_size.bending_pos[0]:
            pos = self.settings.page_size.bending_pos[0][0]
            canvas.line(0, int(height*pos), 10*mm, int(height*pos))
        # 3-part
        if self.settings.page_size.bending_pos[1]:
            for pos in self.settings.page_size.bending_pos[1]:
                canvas.line(0, int(height*pos), 8*mm, int(height*pos))
        canvas.restoreState()

    def header(self, canvas, document):
        pass

    def footer(self, canvas, document):
        # Page footer
        # Line
        canvas.saveState()
        canvas.setLineWidth(0.2)
        canvas.setLineCap(1)
        canvas.setStrokeColor(self.settings.hex_base_color)
        canvas.line(
            document.leftMargin,
            document.bottomMargin - 7*mm,
            document._rightMargin,
            document.bottomMargin - 7*mm
        )
        canvas.restoreState()

        # Page numbering
        canvas.saveState()
        numbering = Paragraph(_("Page %(current)d on %(total)d") % self.doc.page_index(), style=self.style['PageNumbering'])
        available_width, available_height = (25*mm, document.bottomMargin - 9*mm)
        w, h = numbering.wrap(available_width, available_height)
        numbering.drawOn(canvas, document._rightMargin - w, available_height - h)
        canvas.restoreState()

    def p(self, text, style=None):
        self.story.append(Paragraph(text, style or self.style['p']))

    def h1(self, text, style=None):
        self.story.append(Paragraph(text, style or self.style['h1']))

    def h2(self, text, style=None):
        self.story.append(Paragraph(text, style or self.style['h2']))

    def small(self, text, style=None):
        self.story.append(Paragraph(text, style or self.style['Small']))

    def smaller(self, text, style=None):
        self.story.append(Paragraph(text, style or self.style['Smaller']))

    def spacer(self, height=6 * mm):
        self.story.append(Spacer(1, height))

    def table(self, data, col_widths=None, style=None, **kwargs):
        self.story.append(Table(data, col_widths, style=style or self.style['Table'], **kwargs))

    def hr(self):
        self.story.append(HRFlowable(width='100%', thickness=0.2, color=base_colors.black))

    def hr_mini(self):
        self.story.append(HRFlowable(width='100%', thickness=0.2, color=base_colors.grey))

    def pagebreak(self):
        self.story.append(PageBreak())

    def append(self, data):
        self.story.append(data)

    def generate(self):
        self.init_report()
        self.fill()
        self.set_metadata()
        self.doc.multiBuild(self.story)

    def draw_svg(self, canvas, path, xpos=0, ypos=0, xsize=None, ysize=None):
        from reportlab.graphics import renderPDF
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(path)
        xL, yL, xH, yH = drawing.getBounds()

        if xsize:
            drawing.renderScale = xsize / (xH - xL)
        if ysize:
            drawing.renderScale = ysize / (yH - yL)

        renderPDF.draw(drawing, canvas, xpos, ypos, showBoundary=self.show_boundaries)

    def next_frame(self):
        self.story.append(CondPageBreak(20 * cm))

    def start_keeptogether(self):
        self.keeptogether_index = len(self.story)

    def end_keeptogether(self):
        keeptogether = KeepTogether(self.story[self.keeptogether_index:])
        self.story = self.story[:self.keeptogether_index]
        self.story.append(keeptogether)
