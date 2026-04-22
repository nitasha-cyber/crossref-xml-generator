from io import BytesIO
import zipfile
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from config import APP_NAME, APP_VERSION, FRONTEND_DIR
from generators import (
    BookGenerator,
    JournalGenerator,
    PostedContentGenerator,
    ProceedingGenerator,
    ReportGenerator,
)
from generators.base import BaseGenerator
from parsers import parse_excel_file
from utils import is_valid_doi, is_valid_orcid


class MetadataEntry(BaseModel):
    content_type: Literal["book", "journal", "report", "proceeding", "posted_content"] = "book"
    title: str = Field(min_length=1)
    doi: str = Field(min_length=3)
    publication_year: int
    author: str | None = None
    orcid: str | None = None
    abstract: str | None = None
    license_url: str | None = None

    publisher: str | None = None
    isbn: str | None = None

    journal_title: str | None = None
    issn: str | None = None
    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None

    institution: str | None = None
    report_number: str | None = None

    conference_name: str | None = None
    conference_location: str | None = None

    posted_content_type: str | None = "preprint"

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str):
        if not is_valid_doi(value):
            raise ValueError("Invalid DOI format")
        return value.strip()

    @field_validator("orcid")
    @classmethod
    def validate_orcid(cls, value: str | None):
        if value and not is_valid_orcid(value):
            raise ValueError("Invalid ORCID format (expected 0000-0000-0000-0000)")
        return value.strip() if value else value


class GenerationRequest(BaseModel):
    entries: list[MetadataEntry]


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GENERATORS = {
    "book": BookGenerator(),
    "journal": JournalGenerator(),
    "report": ReportGenerator(),
    "proceeding": ProceedingGenerator(),
    "posted_content": PostedContentGenerator(),
}


@app.get("/")
def get_frontend():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_file)


@app.get("/css/{filename}")
def get_css(filename: str):
    file_path = FRONTEND_DIR / "css" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="CSS file not found")
    return FileResponse(file_path)


@app.get("/js/{filename}")
def get_js(filename: str):
    file_path = FRONTEND_DIR / "js" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="JS file not found")
    return FileResponse(file_path)


@app.post("/api/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx/.xls)")

    content = await file.read()
    try:
        rows = parse_excel_file(content)
        return {"rows": rows, "count": len(rows)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc


def build_xml(entries: list[MetadataEntry]) -> bytes:
    if not entries:
        raise HTTPException(status_code=400, detail="At least one entry is required")

    root, body = BaseGenerator.create_root()
    for entry in entries:
        GENERATORS[entry.content_type].add_to_body(body, entry.model_dump(exclude_none=True))
    return BaseGenerator.to_xml_bytes(root)


@app.post("/api/generate-xml")
def generate_xml(payload: GenerationRequest):
    xml = build_xml(payload.entries)
    return {"xml": xml.decode("utf-8"), "count": len(payload.entries)}


@app.post("/api/download-xml")
def download_xml(payload: GenerationRequest):
    if len(payload.entries) == 1:
        xml = build_xml(payload.entries)
        return StreamingResponse(
            BytesIO(xml),
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=crossref.xml"},
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for index, entry in enumerate(payload.entries, start=1):
            xml = build_xml([entry])
            safe_type = entry.content_type.replace(" ", "_")
            zip_file.writestr(f"crossref_{safe_type}_{index}.xml", xml)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=crossref_xml_batch.zip"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
