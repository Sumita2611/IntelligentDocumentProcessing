import io
import shutil
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, List, Optional
import time

# Try importing pytesseract
try:
    import pytesseract
    # Check default Windows path if not in PATH
    tess_exe = shutil.which("tesseract")
    if not tess_exe:
        import os
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
        ]
        for p in possible_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                tess_exe = p
                break
    HAS_TESSERACT = tess_exe is not None
except Exception:
    HAS_TESSERACT = False

# Try importing RapidOCR
try:
    from rapidocr import RapidOCR
    RAPID_OCR_INSTANCE = None
    HAS_RAPID_OCR = True
except Exception:
    HAS_RAPID_OCR = False
    RAPID_OCR_INSTANCE = None

def get_rapid_ocr():
    global RAPID_OCR_INSTANCE
    if RAPID_OCR_INSTANCE is None and HAS_RAPID_OCR:
        RAPID_OCR_INSTANCE = RapidOCR()
    return RAPID_OCR_INSTANCE


class ImageService:
    @staticmethod
    def is_tesseract_available() -> bool:
        return HAS_TESSERACT

    @staticmethod
    def preprocess_image(pil_img: Image.Image, enhance: bool = True) -> Image.Image:
        """Apply noise reduction, contrast stretching, and optional sharpening."""
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        # Upscale small images for clearer text detection
        w, h = pil_img.size
        if w < 1000 or h < 1000:
            scale = max(2.0, min(3.0, 1500.0 / max(w, h)))
            new_w = int(w * scale)
            new_h = int(h * scale)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        if enhance:
            # Contrast boost
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.4)
            # Sharpness boost
            enhancer_sharp = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer_sharp.enhance(1.3)

        return pil_img

    @staticmethod
    def extract_with_tesseract(pil_img: Image.Image) -> Dict[str, Any]:
        """Extract text using Tesseract OCR if available."""
        if not HAS_TESSERACT:
            raise RuntimeError("Tesseract OCR binary is not installed or not found on PATH.")

        start_time = time.time()
        text = pytesseract.image_to_string(pil_img)
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)

        confidences = []
        lines = []
        for i in range(len(data.get("text", []))):
            word = data["text"][i].strip()
            conf = float(data["conf"][i])
            if word and conf > 0:
                confidences.append(conf)

        avg_conf = round(sum(confidences) / len(confidences), 1) if confidences else 90.0
        elapsed = round(time.time() - start_time, 3)

        return {
            "text": text.strip(),
            "confidence_score": avg_conf,
            "engine_used": "Tesseract OCR",
            "elapsed": elapsed
        }

    @staticmethod
    def extract_with_rapid_ocr(pil_img: Image.Image) -> Dict[str, Any]:
        """Extract text using high-accuracy RapidOCR engine (ONNX Runtime)."""
        engine = get_rapid_ocr()
        if engine is None:
            raise RuntimeError("RapidOCR engine is not available.")

        start_time = time.time()
        np_img = np.array(pil_img)
        out = engine(np_img)
        elapsed = round(time.time() - start_time, 3)

        txts = getattr(out, "txts", []) or []
        scores = getattr(out, "scores", []) or []
        boxes = getattr(out, "boxes", [])

        conf_list = [float(s) * 100.0 for s in scores if s is not None]
        avg_conf = round(sum(conf_list) / len(conf_list), 1) if conf_list else 95.0

        full_text = "\n".join(txts)

        line_details = []
        for idx, t in enumerate(txts):
            score = round(scores[idx] * 100.0, 1) if idx < len(scores) else 95.0
            box = boxes[idx].tolist() if idx < len(boxes) and hasattr(boxes[idx], "tolist") else []
            line_details.append({
                "text": t,
                "confidence": score,
                "box": box
            })

        return {
            "text": full_text,
            "confidence_score": avg_conf,
            "engine_used": "Docling / RapidOCR",
            "lines": line_details,
            "boxes": boxes,
            "scores": scores,
            "txts": txts,
            "elapsed": elapsed
        }

    @classmethod
    def reconstruct_table_from_ocr(cls, txts: List[str], boxes: Any, img_width: int, img_height: int) -> Optional[Dict[str, Any]]:
        """Reconstruct structured table rows and columns from OCR bounding boxes and text."""
        if not txts or boxes is None or len(txts) < 2:
            return None

        items = []
        for i, text in enumerate(txts):
            if i < len(boxes):
                box = boxes[i]
                # box is 4 points: [[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
                try:
                    xs = [pt[0] for pt in box]
                    ys = [pt[1] for pt in box]
                    center_x = sum(xs) / len(xs)
                    center_y = sum(ys) / len(ys)
                    min_y = min(ys)
                    items.append({
                        "text": text.strip(),
                        "x": center_x,
                        "y": center_y,
                        "min_y": min_y,
                        "box": box
                    })
                except Exception:
                    continue

        if not items:
            return None

        # Sort items primarily by Y (line) with vertical tolerance
        # Compute median line height
        items_sorted_y = sorted(items, key=lambda it: it["y"])
        # Cluster into rows
        rows_grouped: List[List[Dict[str, Any]]] = []
        current_row = [items_sorted_y[0]]

        y_threshold = max(15.0, img_height * 0.025)

        for item in items_sorted_y[1:]:
            last_y = current_row[-1]["y"]
            if abs(item["y"] - last_y) <= y_threshold:
                current_row.append(item)
            else:
                rows_grouped.append(current_row)
                current_row = [item]
        if current_row:
            rows_grouped.append(current_row)

        # Sort each row horizontally by X
        table_rows = []
        for row in rows_grouped:
            sorted_row = sorted(row, key=lambda it: it["x"])
            table_rows.append([it["text"] for it in sorted_row])

        if len(table_rows) >= 2:
            headers = table_rows[0]
            data_rows = table_rows[1:]
            # normalize columns count
            max_cols = max(len(r) for r in table_rows)
            norm_headers = [headers[i] if i < len(headers) else f"Column {i+1}" for i in range(max_cols)]
            norm_rows = []
            for r in data_rows:
                row_padded = [r[i] if i < len(r) else "" for i in range(max_cols)]
                norm_rows.append(row_padded)

            return {
                "id": 1,
                "title": "Detected Table Layout",
                "columns": norm_headers,
                "rows": norm_rows,
                "row_count": len(norm_rows),
                "col_count": max_cols
            }
        return None

    @classmethod
    def process_image(cls, content: bytes, filename: str, is_table: bool = False, engine_preference: str = "automatic") -> Dict[str, Any]:
        """Process image file and extract text and layout."""
        pil_img = Image.open(io.BytesIO(content))
        orig_w, orig_h = pil_img.size

        # Preprocess
        processed_img = cls.preprocess_image(pil_img, enhance=True)

        engine_name = "RapidOCR"
        ocr_result = None

        if engine_preference == "tesseract" and cls.is_tesseract_available():
            try:
                ocr_result = cls.extract_with_tesseract(processed_img)
                engine_name = "Tesseract OCR"
            except Exception:
                pass

        if ocr_result is None:
            # Use RapidOCR / Docling OCR
            ocr_result = cls.extract_with_rapid_ocr(processed_img)
            engine_name = "Docling / RapidOCR"

        tables = []
        if is_table or "table" in filename.lower():
            table = cls.reconstruct_table_from_ocr(
                ocr_result.get("txts", []),
                ocr_result.get("boxes"),
                orig_w,
                orig_h
            )
            if table:
                tables.append(table)

        return {
            "text": ocr_result.get("text", ""),
            "confidence_score": ocr_result.get("confidence_score", 95.0),
            "routed_engine": engine_name,
            "lines": ocr_result.get("lines", []),
            "tables": tables,
            "metadata": {
                "original_dimensions": [orig_w, orig_h],
                "format": pil_img.format or "IMAGE",
                "mode": pil_img.mode,
                "words_extracted": len(ocr_result.get("text", "").split()),
                "engine": engine_name
            }
        }
