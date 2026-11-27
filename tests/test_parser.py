
import pymupdf
import pytest

from career_assistant.document.pdf_parser import PDFParser


def create_test_pdf():

    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Candidate Profile - Python SQL Docker"
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes


def test_pdf_extraction():

    pdf_bytes = create_test_pdf()

    result = PDFParser.extract_text(pdf_bytes)

    assert "Python" in result["text"]
    assert result["page_count"] == 1
    assert result["character_count"] > 0


def test_empty_pdf():

    with pytest.raises(ValueError):
        PDFParser.extract_text(b"")


def test_invalid_pdf():

    with pytest.raises(ValueError):
        PDFParser.extract_text(b"this is not a PDF")
