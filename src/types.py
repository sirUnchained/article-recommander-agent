from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailPage:
    id: int
    subject: str
    sender: str
    body: str


@dataclass
class LinkPage:
    title: str
    link: str


@dataclass
class PaperInfo:
    title: str
    link: str
    abstract: Optional[str] = None
    tldr: Optional[str] = None
    venue: Optional[str] = None
    citation_count: Optional[int] = None
    pdf_url: Optional[str] = None
    source: Optional[str] = None
