from pathlib import Path
import zipfile
from importers.ebook_importer import _read_epub, _split_text, _read_txt

def test_split_txt_into_multiple_reader_pages():
    pages = _split_text("A " * 4000)
    assert len(pages) > 1
    assert all(p["type"] == "text" for p in pages)

def test_epub_parser_reads_spine_order(tmp_path):
    epub = tmp_path / "book.epub"
    container = """<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>"""
    opf = """<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Demo</dc:title><dc:creator>Author</dc:creator></metadata><manifest><item id="a" href="a.xhtml" media-type="application/xhtml+xml"/><item id="b" href="b.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="b"/><itemref idref="a"/></spine></package>"""
    with zipfile.ZipFile(epub, "w") as z:
        z.writestr("META-INF/container.xml", container)
        z.writestr("OPS/content.opf", opf)
        z.writestr("OPS/a.xhtml", "<html><body><p>FIRST</p></body></html>")
        z.writestr("OPS/b.xhtml", "<html><body><h1>SECOND</h1></body></html>")
    title, author, sections = _read_epub(epub)
    assert (title, author) == ("Demo", "Author")
    assert [s["content"] for s in sections] == ["SECOND", "FIRST"]

def test_pdf_selected_from_ebook_menu_is_forwarded_without_reprompt(tmp_path, monkeypatch):
    from importers import ebook_importer
    from importers import pdf_importer

    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-placeholder")
    monkeypatch.setattr(ebook_importer, "scan_ebook_files", lambda: [pdf])
    monkeypatch.setattr("builtins.input", lambda _prompt: "1")

    received = []
    monkeypatch.setattr(
        pdf_importer,
        "handle_pdf_import",
        lambda pdf_path=None: received.append(pdf_path) or True,
    )

    assert ebook_importer.handle_ebook_import() is True
    assert received == [str(pdf.resolve())]


def test_epub_parser_unquotes_encoded_resource_hrefs(tmp_path):
    epub = tmp_path / "encoded.epub"
    container = """<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns/container"><rootfiles><rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>"""
    opf = """<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Encoded</dc:title></metadata><manifest><item id="a" href="chapter%201.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="a"/></spine></package>"""
    with zipfile.ZipFile(epub, "w") as z:
        z.writestr("META-INF/container.xml", container)
        z.writestr("OPS/content.opf", opf)
        z.writestr("OPS/chapter 1.xhtml", "<html><body><p>ENCODED RESOURCE OK</p></body></html>")
    title, author, sections = _read_epub(epub)
    assert title == "Encoded"
    assert sections[0]["content"] == "ENCODED RESOURCE OK"
