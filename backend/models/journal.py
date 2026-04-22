from typing import Optional
from pydantic import BaseModel


class JournalMetadata(BaseModel):
    content_type: str = "journal"
    title: str
    doi: str
    publication_year: int
    author: Optional[str] = None
    orcid: Optional[str] = None
    abstract: Optional[str] = None
    license_url: Optional[str] = None
    publisher: Optional[str] = None
    journal_title: Optional[str] = None
    issn: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    first_page: Optional[str] = None
    last_page: Optional[str] = None
