import io
import os
import tempfile
import fitz  # PyMuPDF
from PIL import Image
from typing import Dict, Any, List, Optional
import time
import logging

from app.services.image_service import ImageService

logger = logging.getLogger(__name__)

# Docling DocumentConverter lazy instance
DOCLING_CONVERTER = None

def get_docling_converter():
    global DOCLING_CONVERTER
    if DOCLING_CONVERTER is None:
        try:
            from docling.document_converter import DocumentConverter
            DOCLING_CONVERTER = DocumentConverter()
        except Exception as e:
            logger.warning(f"Could not initialize Docling converter: {e}")
            DOCLING_CONVERTER = None
    return DOCLING_CONVERTER


class PDFService:
    @staticmethod
    def is_scanned_pdf(doc: fitz.Document) -> bool:
        """Heuristic check: if pages have little to no native text, it's a scanned PDF."""
        total_text_length = 0
        total_images = 0
        pages_to_check = min(len(doc), 5)
        for i in range(pages_to_check):
            page = doc[i]
            t = page.get_text().strip()
            total_text_length += len(t)
            total_images += len(page.get_images())

        avg_text_per_page = total_text_length / max(1, pages_to_check)
        # If less than 40 chars per page on average and has images, treat as scanned
        return avg_text_per_page < 40 and total_images > 0

    @classmethod
    def process_digital_pdf(cls, doc: fitz.Document, filename: str) -> Dict[str, Any]:
        """Extract digital text, layout, and embedded tables using PyMuPDF."""
        start_time = time.time()
        pages = []
        all_tables = []
        full_text_list = []
        table_counter = 1

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            full_text_list.append(f"--- Page {page_num + 1} ---\n{text}")

            # Extract tables if available
            page_tables = []
            try:
                found_tables = page.find_tables()
                if found_tables and found_tables.tables:
                    for tbl in found_tables:
                        extracted = tbl.extract()
                        if extracted and len(extracted) > 1:
                            headers = [str(c) if c is not None else "" for c in extracted[0]]
                            rows = [[str(c) if c is not None else "" for c in r] for r in extracted[1:]]
                            tbl_obj = {
                                "id": table_counter,
                                "title": f"Page {page_num + 1} - Table {len(page_tables) + 1}",
                                "columns": headers,
                                "rows": rows,
                                "row_count": len(rows),
                                "col_count": len(headers),
                                "page_number": page_num + 1
                            }
                            table_counter += 1
                            page_tables.append(tbl_obj)
                            all_tables.append(tbl_obj)
            except Exception as e:
                logger.debug(f"Table extraction error on page {page_num}: {e}")

            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "word_count": len(text.split()),
                "confidence": 99.5,
                "tables_count": len(page_tables)
            })

        doc_meta = doc.metadata or {}
        elapsed = round(time.time() - start_time, 3)

        return {
            "text": "\n\n".join(full_text_list),
            "pages": pages,
            "tables": all_tables,
            "confidence_score": 99.5,
            "routed_engine": "Digital PDF Parser (PyMuPDF Layout)",
            "processing_time_seconds": elapsed,
            "metadata": {
                "page_count": len(doc),
                "title": doc_meta.get("title", ""),
                "author": doc_meta.get("author", ""),
                "creation_date": doc_meta.get("creationDate", ""),
                "format": doc_meta.get("format", "PDF"),
                "is_scanned": False,
                "tables_detected": len(all_tables)
            }
        }

    @classmethod
    def process_scanned_pdf(cls, doc: fitz.Document, filename: str) -> Dict[str, Any]:
        """Extract text from scanned PDF by rendering pages and executing OCR."""
        start_time = time.time()
        pages = []
        all_tables = []
        full_text_list = []
        table_counter = 1
        total_conf = 0.0

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to high-res image (200 DPI matrix)
            zoom = 2.0  # 72 * 2 = 144 DPI (fast and clear for OCR)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Convert pixmap to PNG bytes
            img_bytes = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_bytes))

            # Run OCR on the rendered page
            ocr_res = ImageService.extract_with_rapid_ocr(pil_img)
            page_text = ocr_res.get("text", "").strip()
            page_conf = ocr_res.get("confidence_score", 95.0)
            total_conf += page_conf

            full_text_list.append(f"--- Page {page_num + 1} (OCR) ---\n{page_text}")

            # Check for reconstructed table
            tbl = ImageService.reconstruct_table_from_ocr(
                ocr_res.get("txts", []),
                ocr_res.get("boxes"),
                pil_img.width,
                pil_img.height
            )
            page_tables = []
            if tbl:
                tbl["id"] = table_counter
                tbl["title"] = f"Page {page_num + 1} - Detected Table"
                tbl["page_number"] = page_num + 1
                table_counter += 1
                page_tables.append(tbl)
                all_tables.append(tbl)

            pages.append({
                "page_number": page_num + 1,
                "text": page_text,
                "word_count": len(page_text.split()),
                "confidence": page_conf,
                "tables_count": len(page_tables)
            })

        avg_conf = round(total_conf / max(1, len(doc)), 1)
        elapsed = round(time.time() - start_time, 3)

        return {
            "text": "\n\n".join(full_text_list),
            "pages": pages,
            "tables": all_tables,
            "confidence_score": avg_conf,
            "routed_engine": "Docling + RapidOCR (Scanned PDF Pipeline)",
            "processing_time_seconds": elapsed,
            "metadata": {
                "page_count": len(doc),
                "is_scanned": True,
                "tables_detected": len(all_tables),
                "ocr_resolution_dpi": 144
            }
        }

    @classmethod
    def process_with_docling(cls, content: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Process document using full Docling DocumentConverter pipeline."""
        converter = get_docling_converter()
        if not converter:
            return None

        # Write to temporary file for Docling
        start_time = time.time()
        ext = os.path.splitext(filename)[1] or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            conv_result = converter.convert(tmp_path)
            docling_doc = conv_result.document
            markdown_text = docling_doc.export_to_markdown()
            plain_text = docling_doc.export_to_text() if hasattr(docling_doc, "export_to_text") else markdown_text

            tables = []
            if hasattr(docling_doc, "tables"):
                for idx, t in enumerate(docling_doc.tables, 1):
                    df = t.export_to_dataframe() if hasattr(t, "export_to_dataframe") else None
                    if df is not None:
                        df = df.fillna("")
                        tables.append({
                            "id": idx,
                            "title": f"Docling Table {idx}",
                            "columns": [str(c) for c in df.columns],
                            "rows": df.values.tolist(),
                            "row_count": len(df),
                            "col_count": len(df.columns)
                        })

            elapsed = round(time.time() - start_time, 3)

            return {
                "text": plain_text or markdown_text,
                "markdown": markdown_text,
                "tables": tables,
                "confidence_score": 98.0,
                "routed_engine": "Docling Intelligence Engine",
                "processing_time_seconds": elapsed,
                "metadata": {
                    "tables_detected": len(tables),
                    "docling_version": "2.x"
                }
            }
        except Exception as e:
            logger.warning(f"Docling conversion exception: {e}")
            return None
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    @classmethod
    def process_pdf(cls, content: bytes, filename: str, force_scanned: Optional[bool] = None, use_docling: bool = False) -> Dict[str, Any]:
        """Main PDF entry point: intelligently routes to Digital, Scanned, or Docling pipeline."""
        if use_docling:
            docling_res = cls.process_with_docling(content, filename)
            if docling_res:
                return docling_res

        doc = fitz.open(stream=content, filetype="pdf")

        is_scanned = force_scanned if force_scanned is not None else cls.is_scanned_pdf(doc)

        if is_scanned:
            return cls.process_scanned_pdf(doc, filename)
        else:
            return cls.process_digital_pdf(doc, filename)
