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


@dataclass
class ChosenArticleStructure:
    title: str = "LLM BUG"
    decision: str = "LLM BUG"
    relevance_score: int = 0
    technical_interest_score: int = 0
    research_value_score: int = 0
    confidence: int = 0
    relevant_topics: list[str] = []
    key_evidence: str = "LLM BUG"
    reason: str = "LLM BUG"
    needs_further_search: bool = False
    search_for: str = "LLM BUG"
    direct_link: str = "LLM BUG"
