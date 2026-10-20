import os
import time
from typing import Dict, Any, Optional

from app.services.pdf_service import PDFService
from app.services.image_service import ImageService
from app.services.handwriting_service import HandwritingService
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.exporters import export_to_markdown

SUPPORTED_TYPES = {
    "automatic": {
        "label": "Automatic detection",
        "description": "Auto-detect document type and route to optimal pipeline",
        "extensions": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp", ".xlsx", ".xls", ".csv"]
    },
    "scanned_pdf": {
        "label": "Scanned PDF",
        "description": "OCR + document layout extraction for scanned documents",
        "extensions": [".pdf"]
    },
    "digital_pdf": {
        "label": "Digital PDF",
        "description": "Direct text extraction + native layout and table parsing",
        "extensions": [".pdf"]
    },
    "handwritten_image": {
        "label": "Handwritten image",
        "description": "TrOCR transformer recognition for handwritten text",
        "extensions": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]
    },
    "printed_image": {
        "label": "Printed image",
        "description": "Tesseract or Docling OCR for printed document images",
        "extensions": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]
    },
    "excel_csv": {
        "label": "Excel / CSV",
        "description": "Direct spreadsheet parser for sheets, cells, and tables",
        "extensions": [".xlsx", ".xls", ".csv"]
    },
    "table_image": {
        "label": "Image of a table",
        "description": "OCR + table boundary reconstruction into rows and columns",
        "extensions": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]
    }
}


def human_size(bytes_val: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


class DocumentRouter:
    @staticmethod
    def get_supported_types() -> Dict[str, Any]:
        return SUPPORTED_TYPES

    @staticmethod
    def validate_file(filename: str, doc_type: str) -> Optional[str]:
        """Validate filename extension against selected document type."""
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            return "File does not have a recognizable file extension."

        type_info = SUPPORTED_TYPES.get(doc_type)
        if not type_info:
            return f"Unsupported document type requested: '{doc_type}'."

        allowed_exts = type_info["extensions"]
        if ext not in allowed_exts:
            allowed_str = ", ".join(allowed_exts)
            return (
                f"File '{filename}' ({ext}) does not match the selected document type '{type_info['label']}'. "
                f"Allowed extensions for this type are: {allowed_str}"
            )
        return None

    @classmethod
    def route_and_extract(
        cls,
        content: bytes,
        filename: str,
        doc_type: str = "automatic",
        engine_preference: str = "automatic"
    ) -> Dict[str, Any]:
        """Validate, route to appropriate processing engine, and assemble unified result."""
        start_time = time.time()
        file_size = len(content)

        if not content:
            raise ValueError("Uploaded file is empty (0 bytes).")

        # Validation
        validation_error = cls.validate_file(filename, doc_type)
        if validation_error:
            raise ValueError(validation_error)

        ext = os.path.splitext(filename)[1].lower()
        effective_type = doc_type

        # Auto-detect if needed
        if effective_type == "automatic":
            if ext == ".pdf":
                # Quick inspection to classify as digital or scanned
                try:
                    import fitz
                    sample_doc = fitz.open(stream=content, filetype="pdf")
                    if PDFService.is_scanned_pdf(sample_doc):
                        effective_type = "scanned_pdf"
                    else:
                        effective_type = "digital_pdf"
                    sample_doc.close()
                except Exception:
                    effective_type = "scanned_pdf"
            elif ext in [".xlsx", ".xls", ".csv"]:
                effective_type = "excel_csv"
            elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]:
                # Check filename keywords
                lower_name = filename.lower()
                if "handwritten" in lower_name or "hw" in lower_name or "note" in lower_name:
                    effective_type = "handwritten_image"
                elif "table" in lower_name or "grid" in lower_name or "invoice" in lower_name:
                    effective_type = "table_image"
                else:
                    effective_type = "printed_image"

        result = {}
        use_docling = engine_preference in ["docling"]

        # Route to appropriate service
        if effective_type == "digital_pdf":
            result = PDFService.process_pdf(content, filename, force_scanned=False, use_docling=use_docling)
        elif effective_type == "scanned_pdf":
            result = PDFService.process_pdf(content, filename, force_scanned=True, use_docling=use_docling)
        elif effective_type == "handwritten_image":
            result = HandwritingService.process_handwritten_image(content, filename)
        elif effective_type == "table_image":
            result = ImageService.process_image(content, filename, is_table=True, engine_preference=engine_preference)
        elif effective_type == "printed_image":
            result = ImageService.process_image(content, filename, is_table=False, engine_preference=engine_preference)
        elif effective_type == "excel_csv":
            if ext == ".csv":
                result = SpreadsheetService.parse_csv(content, filename)
            else:
                result = SpreadsheetService.parse_excel(content, filename)
            result["routed_engine"] = "Spreadsheet & Tabular Engine (openpyxl + pandas)"
        else:
            raise ValueError(f"Unknown document routing type: {effective_type}")

        elapsed = round(time.time() - start_time, 3)

        # Build unified response
        unified = {
            "success": True,
            "filename": filename,
            "file_size": file_size,
            "file_size_human": human_size(file_size),
            "requested_type": doc_type,
            "detected_type": effective_type,
            "detected_type_label": SUPPORTED_TYPES.get(effective_type, {}).get("label", effective_type),
            "routed_engine": result.get("routed_engine", "OmniOCR Core Pipeline"),
            "confidence_score": result.get("confidence_score", 95.0),
            "processing_time_seconds": elapsed,
            "text": result.get("text", ""),
            "pages": result.get("pages", []),
            "tables": result.get("tables", []),
            "lines": result.get("lines", []),
            "metadata": result.get("metadata", {}),
            "word_count": len(result.get("text", "").split()),
            "character_count": len(result.get("text", ""))
        }

        # Ensure Markdown is populated
        if not result.get("markdown"):
            unified["markdown"] = export_to_markdown(unified)
        else:
            unified["markdown"] = result["markdown"]

        return unified
