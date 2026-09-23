from typing import TypedDict

from src.types import PaperInfo, EmailPage


class AgentState(TypedDict):
    emails: list[EmailPage]

    papers: list[PaperInfo]
    papers_limit: int

    recommendations: list[str]
