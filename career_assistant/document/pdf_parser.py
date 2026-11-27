
import pymupdf


class PDFParser:

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> dict:

        if not pdf_bytes:
            raise ValueError("The uploaded PDF is empty.")

        try:
            document = pymupdf.open(
                stream=pdf_bytes,
                filetype="pdf"
            )

            if document.page_count == 0:
                raise ValueError("The PDF contains no pages.")

            pages = []

            for page_number, page in enumerate(document):
                text = page.get_text("text")

                pages.append({
                    "page": page_number + 1,
                    "text": text.strip()
                })

            document.close()

            full_text = "\n".join(
                page["text"] for page in pages
            )

            if not full_text.strip():
                raise ValueError(
                    "No readable text found. "
                    "The PDF may require OCR."
                )

            return {
                "text": full_text,
                "pages": pages,
                "page_count": len(pages),
                "character_count": len(full_text)
            }

        except pymupdf.FileDataError as error:
            raise ValueError(
                f"Invalid PDF document: {error}"
            ) from error
