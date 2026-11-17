"""PDF rendering contract tests."""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from oc_worker.errors import PermanentFailure
from oc_worker.pdf import extract_pdf_pages


def test_extract_pdf_pages_renders_ordered_jpegs(tmp_path: Path) -> None:
    pdf_path = tmp_path / "reference.pdf"
    pages = []
    for index in range(2):
        page = Image.new("RGB", (320, 240), "white")
        draw = ImageDraw.Draw(page)
        draw.text((20, 20), f"Page {index + 1}", fill="black")
        pages.append(page)
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:])

    rendered = extract_pdf_pages(pdf_path, tmp_path / "pages", max_width=640)

    assert [page["pageNumber"] for page in rendered] == [1, 2]
    assert all(Path(page["path"]).is_file() for page in rendered)
    assert all(Path(page["path"]).read_bytes().startswith(b"\xff\xd8") for page in rendered)


def test_extract_pdf_pages_enforces_the_page_limit(tmp_path: Path) -> None:
    pdf_path = tmp_path / "too-long.pdf"
    pages = [Image.new("RGB", (80, 60), "white") for _ in range(3)]
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:])

    with pytest.raises(PermanentFailure, match="limit is 2"):
        extract_pdf_pages(pdf_path, tmp_path / "pages", max_pages=2)
