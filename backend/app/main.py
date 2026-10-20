import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.extraction import router as extraction_router, SAMPLES_DIR

app = FastAPI(
    title="OmniOCR - Document Intelligence API",
    description="Multi-format document extraction platform powered by Docling, RapidOCR, Tesseract, TrOCR, and OpenPyXL.",
    version="1.0.0"
)

# Configure CORS for all origins (allows Vercel frontend or local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include extraction API routes
app.include_router(extraction_router)

# Mount samples directory for static preview if exists
if os.path.exists(SAMPLES_DIR):
    app.mount("/static/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "engines": {
            "docling": "ready",
            "rapidocr": "ready",
            "pymupdf": "ready",
            "openpyxl": "ready",
            "trocr": "ready"
        }
    }


# Check for built frontend SPA
FRONTEND_DIST = os.environ.get(
    "FRONTEND_DIST_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
)
if not os.path.exists(FRONTEND_DIST):
    # Try alternate location (e.g. root/frontend/dist)
    alt_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
    if os.path.exists(alt_dist):
        FRONTEND_DIST = alt_dist

if os.path.exists(FRONTEND_DIST):
    # Mount assets directory
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Allow /docs, /openapi.json, /api to pass through
        if full_path.startswith("api") or full_path in ["docs", "openapi.json", "redoc"]:
            return None
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "app": "OmniOCR - Document Intelligence",
            "status": "online",
            "docs_url": "/docs",
            "api_prefix": "/api"
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
