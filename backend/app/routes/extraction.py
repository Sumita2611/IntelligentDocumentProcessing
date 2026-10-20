import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.services.document_router import DocumentRouter, SUPPORTED_TYPES
from app.services.image_service import ImageService
from app.utils.exporters import export_to_txt, export_to_json, export_to_markdown, export_to_csv

router = APIRouter(prefix="/api", tags=["Document Extraction"])

# Base samples directory
SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../samples"))


class ExportRequest(BaseModel):
    format: str # 'txt', 'json', 'csv', 'markdown'
    data: Dict[str, Any]


@router.get("/document-types")
def get_document_types():
    """Return all supported document types and metadata."""
    types_list = []
    for key, val in SUPPORTED_TYPES.items():
        types_list.append({
            "key": key,
            "label": val["label"],
            "description": val["description"],
            "extensions": val["extensions"],
            "badge": "Recommended" if key == "automatic" else None
        })
    return {"document_types": types_list}


@router.get("/engines")
def get_engines():
    """Return available processing engines and host capability status."""
    has_tess = ImageService.is_tesseract_available()
    return {
        "engines": [
            {
                "key": "automatic",
                "label": "Automatic — choose the appropriate processing pipeline",
                "status": "active",
                "description": "Smart router dynamically picks Docling, RapidOCR, TrOCR, or Spreadsheet engine"
            },
            {
                "key": "docling",
                "label": "Docling Document Intelligence",
                "status": "active",
                "description": "Unified document parsing, deep layout analysis, and table reconstruction"
            },
            {
                "key": "rapidocr",
                "label": "RapidOCR Deep Engine (ONNX)",
                "status": "active",
                "description": "State-of-the-art neural character detection and text line extraction"
            },
            {
                "key": "tesseract",
                "label": "Tesseract OCR",
                "status": "active" if has_tess else "fallback_active",
                "description": "Classic OCR engine (RapidOCR fallback active)" if not has_tess else "Native Tesseract binary active"
            },
            {
                "key": "trocr",
                "label": "TrOCR (Transformer Handwriting)",
                "status": "active",
                "description": "Hugging Face VisionEncoderDecoder model for handwritten script lines"
            },
            {
                "key": "spreadsheet",
                "label": "openpyxl + pandas Parser",
                "status": "active",
                "description": "High-fidelity native spreadsheet parsing for Excel (.xlsx) and CSV"
            }
        ]
    }


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    document_type: str = Form("automatic"),
    engine: str = Form("automatic")
):
    """Primary document extraction endpoint."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        result = DocumentRouter.route_and_extract(
            content=content,
            filename=file.filename or "uploaded_document",
            doc_type=document_type,
            engine_preference=engine
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.post("/export")
def export_document(req: ExportRequest):
    """Export extracted document in user-selected format."""
    fmt = req.format.lower()
    data = req.data
    filename = data.get("filename", "document")
    base_name = os.path.splitext(filename)[0]

    if fmt == "txt":
        content = export_to_txt(data)
        media_type = "text/plain; charset=utf-8"
        download_name = f"{base_name}_extracted.txt"
    elif fmt == "json":
        content = export_to_json(data)
        media_type = "application/json; charset=utf-8"
        download_name = f"{base_name}_extracted.json"
    elif fmt == "csv":
        content = export_to_csv(data)
        media_type = "text/csv; charset=utf-8"
        download_name = f"{base_name}_extracted.csv"
    elif fmt in ["markdown", "md"]:
        content = export_to_markdown(data)
        media_type = "text/markdown; charset=utf-8"
        download_name = f"{base_name}_extracted.md"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export format '{req.format}'. Use txt, json, csv, or markdown.")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
    )


@router.get("/samples")
def list_samples():
    """List preloaded sample documents for quick live demonstration."""
    samples = [
        {
            "id": "financial_report",
            "filename": "quarterly_financial_report.xlsx",
            "title": "Excel Financial Spreadsheet",
            "doc_type": "excel_csv",
            "description": "Multi-sheet financial model with revenue, balance sheet, and expenses",
            "file_size": "24.5 KB"
        },
        {
            "id": "sales_records",
            "filename": "regional_sales_records.csv",
            "title": "Regional Sales CSV",
            "doc_type": "excel_csv",
            "description": "Tabular CSV dataset with customer orders, units, and profit margins",
            "file_size": "12.8 KB"
        },
        {
            "id": "scanned_invoice",
            "filename": "scanned_medical_invoice.png",
            "title": "Scanned Medical Invoice",
            "doc_type": "scanned_pdf",
            "description": "Scanned invoice with itemized clinical procedures and totals",
            "file_size": "95.2 KB"
        },
        {
            "id": "digital_document",
            "filename": "docling_tech_specification.pdf",
            "title": "Digital Technical Whitepaper",
            "doc_type": "digital_pdf",
            "description": "Multi-page digital PDF with headers, paragraphs, and embedded table",
            "file_size": "48.1 KB"
        },
        {
            "id": "handwritten_rx",
            "filename": "handwritten_prescription_notes.png",
            "title": "Handwritten Doctor Note",
            "doc_type": "handwritten_image",
            "description": "Cursive handwritten clinical prescription notes processed with TrOCR",
            "file_size": "82.4 KB"
        },
        {
            "id": "table_photo",
            "filename": "table_matrix_photo.png",
            "title": "Photograph of Structured Table",
            "doc_type": "table_image",
            "description": "Grid matrix photo reconstructed into rows and columns",
            "file_size": "88.6 KB"
        }
    ]
    return {"samples": samples}


@router.post("/extract-sample/{sample_id}")
def extract_sample(sample_id: str, engine: str = "automatic"):
    """Run extraction on one of the preloaded sample documents."""
    sample_map = {
        "financial_report": ("quarterly_financial_report.xlsx", "excel_csv"),
        "sales_records": ("regional_sales_records.csv", "excel_csv"),
        "scanned_invoice": ("scanned_medical_invoice.png", "printed_image"),
        "digital_document": ("docling_tech_specification.pdf", "digital_pdf"),
        "handwritten_rx": ("handwritten_prescription_notes.png", "handwritten_image"),
        "table_photo": ("table_matrix_photo.png", "table_image")
    }

    if sample_id not in sample_map:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")

    filename, default_type = sample_map[sample_id]
    sample_path = os.path.join(SAMPLES_DIR, filename)

    if not os.path.exists(sample_path):
        raise HTTPException(status_code=500, detail=f"Sample file '{filename}' was not found on disk.")

    with open(sample_path, "rb") as f:
        content = f.read()

    result = DocumentRouter.route_and_extract(
        content=content,
        filename=filename,
        doc_type=default_type,
        engine_preference=engine
    )
    return result
