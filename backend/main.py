from io import BytesIO
from typing import Any
import zipfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import APP_NAME, APP_VERSION, FRONTEND_DIR
from generators import (
    BookGenerator,
    JournalGenerator,
    PostedContentGenerator,
    ProceedingGenerator,
    ReportGenerator,
)
from parsers.excel_parser import parse_excel_file


app = FastAPI(title=APP_NAME, version=APP_VERSION)


class MetadataEntry(BaseModel):
    content_type: str = "journal"
    title: str | None = None
    doi: str = ""
    publication_year: int | None = None
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


class GenerateRequest(BaseModel):
    entries: list[MetadataEntry]


GENERATORS: dict[str, Any] = {
    "book": BookGenerator(),
    "journal": JournalGenerator(),
    "report": ReportGenerator(),
    "proceeding": ProceedingGenerator(),
    "posted_content": PostedContentGenerator(),
}


def _generate_xml_bytes(entry_data: dict) -> bytes:
    content_type = entry_data.get("content_type", "journal")
    generator = GENERATORS.get(content_type)
    if generator is None:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type!r}")
    root, body = generator.create_root()
    generator.add_to_body(body, entry_data)
    return generator.to_xml_bytes(root)


@app.post("/api/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx or .xls).")
    content = await file.read()
    try:
        rows = parse_excel_file(content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse Excel file: {exc}") from exc
    return JSONResponse({"rows": rows, "count": len(rows)})


@app.post("/api/generate-xml")
async def generate_xml(request: GenerateRequest):
    if not request.entries:
        raise HTTPException(status_code=400, detail="No entries provided.")

    if len(request.entries) == 1:
        entry_data = request.entries[0].model_dump(exclude_none=True)
        xml_bytes = _generate_xml_bytes(entry_data)
        return JSONResponse({"xml": xml_bytes.decode("utf-8"), "count": 1})

    xml_parts = []
    for entry in request.entries:
        entry_data = entry.model_dump(exclude_none=True)
        xml_bytes = _generate_xml_bytes(entry_data)
        xml_parts.append(xml_bytes.decode("utf-8"))

    combined = "\n\n".join(xml_parts)
    return JSONResponse({"xml": combined, "count": len(request.entries)})


@app.post("/api/download-xml")
async def download_xml(request: GenerateRequest):
    if not request.entries:
        raise HTTPException(status_code=400, detail="No entries provided.")

    if len(request.entries) == 1:
        entry_data = request.entries[0].model_dump(exclude_none=True)
        xml_bytes = _generate_xml_bytes(entry_data)
        doi_slug = (entry_data.get("doi") or "output").replace("/", "_")
        filename = f"{doi_slug}.xml"
        return Response(
            content=xml_bytes,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, entry in enumerate(request.entries, start=1):
            entry_data = entry.model_dump(exclude_none=True)
            xml_bytes = _generate_xml_bytes(entry_data)
            doi_slug = (entry_data.get("doi") or f"entry_{i}").replace("/", "_")
            zf.writestr(f"{doi_slug}.xml", xml_bytes)
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=crossref_batch.zip"},
    )


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
