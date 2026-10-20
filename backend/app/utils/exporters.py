import io
import csv
import json
from typing import Dict, Any, List

def export_to_txt(data: Dict[str, Any]) -> str:
    """Format extraction result into a clean text document."""
    lines = []
    lines.append("==================================================")
    lines.append(f"OmniOCR - Document Extraction Report")
    lines.append(f"Filename: {data.get('filename', 'Unknown')}")
    lines.append(f"Document Type: {data.get('detected_type', 'Unknown')}")
    lines.append(f"Engine: {data.get('routed_engine', 'Unknown')}")
    if data.get('processing_time_seconds'):
        lines.append(f"Processing Time: {data.get('processing_time_seconds')}s")
    if data.get('confidence_score') is not None:
        lines.append(f"Confidence: {data.get('confidence_score')}%")
    lines.append("==================================================\n")

    # Full text
    lines.append("--- EXTRACTED TEXT ---")
    lines.append(data.get("text", "").strip() or "(No text extracted)")
    lines.append("")

    # Tables if present
    tables: List[Dict[str, Any]] = data.get("tables", [])
    if tables:
        lines.append("\n--- EXTRACTED TABLES ---")
        for i, tbl in enumerate(tables, 1):
            title = tbl.get("title") or f"Table {i}"
            lines.append(f"\n[{title}]")
            headers = tbl.get("columns", [])
            rows = tbl.get("rows", [])
            if headers:
                lines.append(" | ".join(str(h) for h in headers))
                lines.append("-" * 40)
            for r in rows:
                lines.append(" | ".join(str(cell) if cell is not None else "" for cell in r))

    return "\n".join(lines)


def export_to_json(data: Dict[str, Any]) -> str:
    """Return extraction result formatted as indented JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_to_markdown(data: Dict[str, Any]) -> str:
    """Format extraction result into GitHub-flavored Markdown."""
    md = []
    filename = data.get("filename", "Document")
    md.append(f"# Extraction Report: {filename}\n")
    md.append("| Property | Value |")
    md.append("| :--- | :--- |")
    md.append(f"| **Document Type** | `{data.get('detected_type', 'N/A')}` |")
    md.append(f"| **Engine Used** | `{data.get('routed_engine', 'N/A')}` |")
    if data.get("processing_time_seconds"):
        md.append(f"| **Processing Time** | `{data.get('processing_time_seconds')}s` |")
    if data.get("confidence_score") is not None:
        md.append(f"| **Confidence** | `{data.get('confidence_score')}%` |")
    if data.get("pages"):
        md.append(f"| **Total Pages** | `{len(data.get('pages', []))}` |")
    md.append("")

    # Extracted text section
    md.append("## Extracted Text\n")
    pages = data.get("pages", [])
    if pages and len(pages) > 1:
        for p in pages:
            md.append(f"### Page {p.get('page_number', '?')}")
            md.append(p.get("text", "").strip() or "*(No text)*")
            md.append("")
    else:
        text = data.get("text", "").strip()
        md.append(text if text else "*(No text extracted)*")
        md.append("")

    # Tables section
    tables = data.get("tables", [])
    if tables:
        md.append("## Extracted Tables\n")
        for i, tbl in enumerate(tables, 1):
            title = tbl.get("title") or f"Table {i}"
            md.append(f"### {title}\n")
            headers = tbl.get("columns", [])
            rows = tbl.get("rows", [])
            if headers:
                md.append("| " + " | ".join(str(h) for h in headers) + " |")
                md.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for r in rows:
                    cells = [str(c).replace("\n", " ").replace("|", "\\|") if c is not None else "" for c in r]
                    # pad if fewer cells than headers
                    while len(cells) < len(headers):
                        cells.append("")
                    md.append("| " + " | ".join(cells[:len(headers)]) + " |")
                md.append("")

    return "\n".join(md)


def export_to_csv(data: Dict[str, Any]) -> str:
    """Format extracted tables or text lines into CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    tables = data.get("tables", [])
    if tables:
        for i, tbl in enumerate(tables):
            title = tbl.get("title") or f"Table {i + 1}"
            writer.writerow([f"# {title}"])
            headers = tbl.get("columns", [])
            if headers:
                writer.writerow(headers)
            for row in tbl.get("rows", []):
                writer.writerow(row)
            writer.writerow([]) # empty separator row
    else:
        # Fallback to lines of text
        writer.writerow(["Line Number", "Extracted Content"])
        raw_text = data.get("text", "")
        for idx, line in enumerate(raw_text.splitlines(), start=1):
            if line.strip():
                writer.writerow([idx, line.strip()])

    return output.getvalue()
