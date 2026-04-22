from typing import Optional
from pydantic import BaseModel


class ReportMetadata(BaseModel):
    content_type: str = "report"
    title: str
    doi: str
    publication_year: int
    author: Optional[str] = None
    orcid: Optional[str] = None
    abstract: Optional[str] = None
    license_url: Optional[str] = None
    institution: Optional[str] = None
    report_number: Optional[str] = None
