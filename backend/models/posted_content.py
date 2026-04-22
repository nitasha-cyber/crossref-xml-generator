from typing import Optional
from pydantic import BaseModel


class PostedContentMetadata(BaseModel):
    content_type: str = "posted_content"
    title: str
    doi: str
    publication_year: int
    author: Optional[str] = None
    orcid: Optional[str] = None
    abstract: Optional[str] = None
    license_url: Optional[str] = None
    posted_content_type: Optional[str] = "preprint"
    institution: Optional[str] = None
