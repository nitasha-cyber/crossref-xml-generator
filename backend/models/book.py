from typing import Optional
from pydantic import BaseModel


class BookMetadata(BaseModel):
    content_type: str = "book"
    title: str
    doi: str
    publication_year: int
    author: Optional[str] = None
    orcid: Optional[str] = None
    abstract: Optional[str] = None
    license_url: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
