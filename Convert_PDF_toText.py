from io import StringIO
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LTTextBox, LTTextLine, LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from converting_to_HTML import HTMLPrivateConverter


class PdfToText(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.codec = 'utf-8'
        self.scale = 1

    def convert_pdf_to_txt(self, path, page_no=-1):
        resource_manager = PDFResourceManager()
        text_output = StringIO()
        layout_params = LAParams()
        text_converter = TextConverter(resource_manager, text_output, laparams=layout_params)

        with open(path, 'rb') as file:
            pdf_interpreter = PDFPageInterpreter(resource_manager, text_converter)
            current_page = 0
            for page in PDFPage.get_pages(file, set(), maxpages=0, password="", caching=True, check_extractable=True):
                current_page += 1
                if current_page != page_no and page_no != -1:
                    continue
                pdf_interpreter.process_page(page)

        text = text_output.getvalue()
        text_output.close()

        return text

    def read_pdf(self, file_name):
        resource_manager = PDFResourceManager()
        layout_params = LAParams()
        with open(file_name, 'rb') as file:
            parser = PDFParser(file)
            document = PDFDocument(parser)
            device = PDFPageAggregator(resource_manager, laparams=layout_params)
            interpreter = PDFPageInterpreter(resource_manager, device)

            pages = {}
            for page in PDFPage.create_pages(document):
                page_data = {}
                page_data['textbox'] = []
                page_data['textline'] = []

                interpreter.process_page(page)
                layout = device.get_result()
                for item in layout:
                    if isinstance(item, LTTextBox):
                        page_data['textbox'].append(item)
                        for child in item:
                            if isinstance(child, LTTextLine):
                                page_data['textline'].append(child)
                pages[layout.pageid] = page_data
        return pages

    def compare_pdf(self, file1, file2, header_text, x_margin=10, compare_margin=0.2):
        resource_manager = PDFResourceManager()
        retstr = StringIO()
        layout_params = LAParams()
        with open(file1, 'rb') as file:
            parser = PDFParser(file)
            document = PDFDocument(parser)
            device = PDFPageAggregator(resource_manager, laparams=layout_params)

            output = StringIO()
            scale = 1.3
            fontscale = 1

            html_converter = HTMLPrivateConverter(resource_manager, output, scale=scale,
                                                  layoutmode='normal', laparams=layout_params, fontscale=fontscale,
                                                  imagewriter=None, header_text=header_text, x_margin=x_margin)
            interpreter = PDFPageInterpreter(resource_manager, device)
            test_pages = PDFPage.create_pages(document)

            file_dict = self.read_pdf(file2)

            for page in test_pages:
                interpreter.process_page(page)
                layout = device.get_result()

                html_converter.page_begin(layout)
                compare_page = file_dict.get(layout.pageid)
                if compare_page is None:
                    break

                for item in layout:
                    if isinstance(item, LTTextBox):
                        html_converter.begin_div('textbox', 1, item.x0 + html_converter.x_margin, item.y1, item.width,
                                                 item.height, item.get_writing_mode())

                        for child in item:
                            if isinstance(child, LTTextLine):
                                self.compare_textline(child, compare_page, html_converter, compare_margin)
                                html_converter.put_newline()
                        html_converter.end_div()
                html_converter.page_end()

        return output.getvalue()

    def compare_textline(self, child, compare_page, html_coverter, compare_margin):
        comp_result = True
        for comp_textline in compare_page['textline']:
            if child.x0 - compare_margin < comp_textline.x0 and comp_textline.x0 < child.x0 + compare_margin and child.y1 - compare_margin < comp_textline.y1 and comp_textline.y1 < child.y1 + compare_margin:
                if child.get_text() != comp_textline.get_text():
                    html_coverter.put_text_invalid(child.get_text(), child._objs[0].fontname, child._objs[0].size)
                else:
                    html_coverter.put_text(child.get_text(), child._objs[0].fontname, child._objs[0].size)

                comp_result = False
                break

        if comp_result:
            html_coverter.put_text_invalid(child.get_text(), child._objs[0].fontname, child._objs[0].size)

    def convert_list(self, obj):
        list = []
        for child in obj:
            list.append(child)
        return list