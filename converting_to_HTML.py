from pdfminer.converter import PDFConverter

class HTMLPrivateConverter(PDFConverter):
    RECT_COLORS = {
        'figure': 'yellow',
        'textline': 'magenta',
        'textbox': 'cyan',
        'textgroup': 'red',
        'curve': 'black',
        'page': 'gray',
    }

    TEXT_COLORS = {
        'textbox': 'blue',
        'char': 'black',
    }

    def __init__(self, rsrcmgr, outfp, pageno=1, laparams=None,
                 scale=1, fontscale=1.0, layoutmode='normal', showpageno=True,
                 pagemargin=50, imagewriter=None, header_text='', x_margin=0,
                 rect_colors={'curve': 'black', 'page': 'gray'},
                 text_colors={'char': 'black'}):
        super().__init__(rsrcmgr, outfp, pageno=pageno, laparams=laparams)
        self.scale = scale
        self.fontscale = fontscale
        self.layoutmode = layoutmode
        self.showpageno = showpageno
        self.pagemargin = pagemargin
        self.imagewriter = imagewriter
        self.rect_colors = rect_colors
        self.text_colors = text_colors
        self.debug = False
        if self.debug:
            self.rect_colors.update(self.RECT_COLORS)
            self.text_colors.update(self.TEXT_COLORS)
        self._yoffset = self.pagemargin
        self._font = None
        self._ffont = ('AllAndNone', 11)
        self._fontstack = []
        self.header_text = header_text
        self.x_margin = x_margin
        self._write_header()
        return

    def write(self, text):
        self.outfp.write(text)
        return

    def _write_header(self):
        margin_left = 200 if self.x_margin != 10 else 7
        self.write(
            f'<div><span style="position:absolute; color:1; left:{self.x_margin + margin_left}px; top:0px; font-size:{30 * self.scale * 1}px;">')
        self._write_text(self.header_text)
        self.write('</span></div>\n')
        return

    def _write_text(self, text):
        self.write(text)
        return

    def _place_rect(self, color, borderwidth, x, y, w, h):
        color = self.rect_colors.get(color)
        if color is not None:
            self.write(
                f'<span style="position:absolute; border:{color} {borderwidth}px solid; '
                f'left:{x * self.scale}px; top:{(self._yoffset - y) * self.scale}px; width:{w * self.scale}px; height:{h * self.scale}px;"></span>\n')
        return

    def _place_border(self, color, borderwidth, item):
        self._place_rect(color, borderwidth, item.x0 + self.x_margin, item.y1, item.width, item.height)
        return

    # Other methods left as they are for brevity...
