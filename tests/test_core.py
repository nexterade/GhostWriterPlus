import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from importers.pdf_importer import _read_pdf_metadata, _select_pdf_title, _render_pdf_pages
from importers._reader_common import render_reader_html
from parsers.json_parser import JSONChatParser
from importers.chat_url_importer import _find_structured_candidates, _parser_from_object, _extract_embedded_json, normalize_share_url
from importers.chat_importer import _parse_selection, _export_data
from serve import run_server

class CoreTests(unittest.TestCase):
    def test_pdf_title_fallback_and_pages(self):
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest('reportlab unavailable')
        with TemporaryDirectory() as td:
            p = Path(td) / 'Nama Buku Nyata.pdf'
            c = canvas.Canvas(str(p), pagesize=(300, 400)); c.setTitle('Untitled')
            c.drawString(20, 350, 'A'); c.showPage(); c.drawString(20, 350, 'B'); c.showPage(); c.save()
            meta = _read_pdf_metadata(str(p))
            self.assertEqual(meta['pages'], 2)
            self.assertEqual(_select_pdf_title(str(p), meta['title']), 'Nama Buku Nyata')

    def test_json_generic_messages(self):
        with TemporaryDirectory() as td:
            p = Path(td) / 'claude.json'
            p.write_text(json.dumps({'name':'Claude Test','messages':[
                {'role':'user','content':'Halo'}, {'role':'assistant','content':'Hai'}]}), encoding='utf-8')
            parser = JSONChatParser(str(p)); self.assertTrue(parser.validate())
            data = parser.parse(0)
            self.assertEqual(data['title'], 'Claude Test')
            self.assertEqual(len(data['messages']), 2)

    def test_chat_selection_ranges(self):
        self.assertEqual(_parse_selection("all", 4), [0, 1, 2, 3])
        self.assertEqual(_parse_selection("1,3-4", 5), [0, 2, 3])

    def test_share_url_normalization(self):
        raw = '  \"https://chatgpt.com/share/test\"\u200b  '
        self.assertEqual(normalize_share_url(raw), 'https://chatgpt.com/share/test')
        self.assertEqual(normalize_share_url('www.chatgpt.com/share/test'), 'https://www.chatgpt.com/share/test')

    def test_share_url_next_flight_payload(self):
        payload = '{"mapping":{"n1":{"message":{"author":{"role":"user"},"content":{"parts":["Halo"]}}}},"title":"Flight Test"}'
        block = 'self.__next_f.push([1,' + json.dumps(payload) + '])'
        objs = _extract_embedded_json(block)
        self.assertTrue(any(isinstance(x, dict) and 'mapping' in x for x in objs))

    def test_share_url_structured_data(self):
        obj = {"props": {"conversation": {
            "title": "Share Test",
            "messages": [
                {"role": "user", "content": "Halo"},
                {"role": "assistant", "content": "Hai"},
            ]
        }}}
        candidates = _find_structured_candidates(obj)
        self.assertTrue(candidates)
        data = None
        for candidate in candidates:
            data = _parser_from_object(candidate, "https://chatgpt.com/share/test", "ChatGPT")
            if data:
                break
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], "Share Test")
        self.assertEqual(len(data["messages"]), 2)

    def test_pdf_render_all_pages_is_path_independent(self):
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest('reportlab unavailable')
        with TemporaryDirectory() as td:
            root = Path(td)
            pdf = root / 'book.pdf'
            c = canvas.Canvas(str(pdf), pagesize=(300, 400))
            for i in range(1, 9):
                c.drawString(20, 350, f'Page {i}')
                c.showPage()
            c.save()
            out = root / 'images'
            sections, failures = _render_pdf_pages(str(pdf), 8, out)
            self.assertEqual(len(sections), 8)
            self.assertEqual(failures, [])
            self.assertEqual(len(list(out.glob('page_*.jpg'))), 8)

    def test_pdf_render_pipeline_uses_loading_spinner(self):
        import inspect
        from importers import pdf_importer
        source = inspect.getsource(pdf_importer._render_pdf_pages)
        self.assertIn('spinner = LoadingSpinner', source)
        self.assertIn('spinner.update', source)
        self.assertIn('spinner.stop', source)

    def test_chat_export_is_path_independent(self):
        data = {'title': 'Path Test', 'messages': [
            {'role': 'user', 'content': 'Halo', 'timestamp': ''},
            {'role': 'assistant', 'content': 'Hai', 'timestamp': ''},
        ]}
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            test_dir = Path(td) / "history"
            self.assertTrue(_export_data(data, 'unit-test', 1, output_dir=test_dir))
            target = test_dir / 'path-test' / 'index.html'
            self.assertTrue(target.is_file())



    def test_server_accepts_string_public_path(self):
        # Regression guard for v3.0.2: main() passes a string to run_server().
        # The function must normalize it to Path before calling resolve().
        import inspect
        source = inspect.getsource(run_server)
        self.assertIn("public_path = Path(public_path).expanduser().resolve()", source)

    def test_reader_render_has_pages_and_inline_svg(self):
        with TemporaryDirectory() as td:
            out = Path(td) / 'index.html'
            render_reader_html('templates/reader/reader.html', str(out), {
                'title':'Buku Test','author':'Tester','sections':[
                    {'page':1,'type':'image','src':'images/page_001.jpg'},
                    {'page':2,'type':'image','src':'images/page_002.jpg'}]}, 'ebook')
            html = out.read_text(encoding='utf-8')
            self.assertIn('id="stat-pages"', html)
            self.assertIn('<svg', html)
            self.assertIn('Buku Test', html)
            self.assertNotIn('{{', html)

if __name__ == '__main__': unittest.main(verbosity=2)
