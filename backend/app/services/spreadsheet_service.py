import io
import csv
import pandas as pd
import openpyxl
from typing import Dict, Any, List

class SpreadsheetService:
    @staticmethod
    def parse_csv(content: bytes, filename: str) -> Dict[str, Any]:
        """Parse CSV file content with encoding detection and delimiter sniffing."""
        text_content = ""
        encoding_used = "utf-8"
        for enc in ["utf-8-sig", "utf-8", "latin1", "cp1252"]:
            try:
                text_content = content.decode(enc)
                encoding_used = enc
                break
            except UnicodeDecodeError:
                continue

        if not text_content:
            text_content = content.decode("utf-8", errors="replace")

        # Sniff delimiter
        delimiter = ","
        try:
            sniffer = csv.Sniffer()
            sample = text_content[:2048]
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            # Fallback delimiter check
            first_line = text_content.splitlines()[0] if text_content.splitlines() else ""
            if "\t" in first_line:
                delimiter = "\t"
            elif ";" in first_line:
                delimiter = ";"
            elif "|" in first_line:
                delimiter = "|"

        df = pd.read_csv(io.StringIO(text_content), sep=delimiter, dtype=str)
        df = df.fillna("")

        columns = [str(c) for c in df.columns.tolist()]
        rows = df.values.tolist()

        table_obj = {
            "id": 1,
            "title": filename,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "col_count": len(columns),
        }

        # Build readable text
        text_lines = [f"File: {filename} (CSV format, Delimiter: '{delimiter}')", ""]
        text_lines.append("Columns: " + ", ".join(columns))
        text_lines.append(f"Total Rows: {len(rows)}")
        text_lines.append("\n--- Preview Rows ---")
        for r in rows[:15]:
            text_lines.append(" | ".join(str(c) for c in r))
        if len(rows) > 15:
            text_lines.append(f"... and {len(rows) - 15} more rows")

        return {
            "text": "\n".join(text_lines),
            "tables": [table_obj],
            "metadata": {
                "encoding": encoding_used,
                "delimiter": delimiter,
                "sheets_count": 1,
                "total_rows": len(rows),
                "total_columns": len(columns),
            },
            "confidence_score": 100.0,
        }

    @staticmethod
    def parse_excel(content: bytes, filename: str) -> Dict[str, Any]:
        """Parse Excel (.xlsx / .xls) workbook, extracting all sheets as structured tables."""
        file_buffer = io.BytesIO(content)
        excel_file = pd.ExcelFile(file_buffer)
        sheet_names = excel_file.sheet_names

        tables = []
        text_lines = [f"Workbook: {filename}", f"Sheets: {', '.join(sheet_names)}", ""]
        total_rows = 0

        for idx, sheet_name in enumerate(sheet_names, start=1):
            df = pd.read_excel(file_buffer, sheet_name=sheet_name, dtype=str)
            df = df.fillna("")
            columns = [str(c) for c in df.columns.tolist()]
            rows = df.values.tolist()
            total_rows += len(rows)

            table_obj = {
                "id": idx,
                "title": f"Sheet: {sheet_name}",
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "col_count": len(columns),
            }
            tables.append(table_obj)

            text_lines.append(f"=== Sheet: {sheet_name} ({len(rows)} rows, {len(columns)} cols) ===")
            text_lines.append("Columns: " + ", ".join(columns))
            for r in rows[:10]:
                text_lines.append(" | ".join(str(c) for c in r))
            if len(rows) > 10:
                text_lines.append(f"... ({len(rows) - 10} more rows)")
            text_lines.append("")

        return {
            "text": "\n".join(text_lines),
            "tables": tables,
            "metadata": {
                "sheets": sheet_names,
                "sheets_count": len(sheet_names),
                "total_rows": total_rows,
            },
            "confidence_score": 100.0,
        }
