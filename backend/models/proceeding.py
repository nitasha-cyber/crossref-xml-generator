from typing import Optional
from pydantic import BaseModel


class ProceedingMetadata(BaseModel):
    content_type: str = "proceeding"
    title: str
    doi: str
    publication_year: int
    author: Optional[str] = None
    orcid: Optional[str] = None
    abstract: Optional[str] = None
    license_url: Optional[str] = None
    conference_name: Optional[str] = None
    conference_location: Optional[str] = None
