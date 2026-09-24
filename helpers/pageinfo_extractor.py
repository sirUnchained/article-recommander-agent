import requests
from bs4 import BeautifulSoup


from src.types import PaperInfo, LinkPage

import xml.etree.ElementTree as ET
from typing import Optional, List
import re
import logging

logger = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# ---------- arXiv ----------
# most articles are in arxiv, so we need to scrap there!


def _fetch_from_arxiv(link: LinkPage) -> Optional[PaperInfo]:
    """
    Get arxiv article if it exists and scrap them.

    ---

    Args:
        link (str): the link you have.

    Returns:
        PaperInfo | None: the result we could get.
    """

    # searching for arxiv id, if we couldn't find it so we faild to detect article and return none
    match = re.search(r"(\d{4}\.\d{4,5})", link.link)
    arxiv_id = match.group(1) if match else None

    if not arxiv_id:
        return None

    try:
        # simply send request to `export.arxiv.org` for article
        resp = requests.get(
            f"http://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=15
        )
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)

        # if we did not find anything just return none
        if entry is None:
            return None

        # else return data
        abstract = entry.find("atom:summary", ns).text.strip()
        return PaperInfo(
            title=link.title,
            link=link.link,
            abstract=abstract,
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
            source="arxiv",
        )
    except Exception:
        return None


# But most of the articles are behind a powerfull robot detector ...
# so I must somehow get them (i do my best but we cannot get some of them after all)

# ---------- Semantic Scholar ----------


def _fetch_from_semantic_scholar(link: LinkPage) -> Optional[PaperInfo]:
    """
    Get article informations from Semantic Scholar API by searching the title.

    ---

    Args:
        link (str): the link you have.

    Returns:
        PaperInfo | None: the result we could get.
    """

    try:
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": link.title,
                "fields": "title,abstract,tldr,venue,citationCount,openAccessPdf",
                "limit": 1,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None

        results = resp.json().get("data", [])
        if not results:
            return None

        paper = results[0]
        if not paper.get("abstract"):
            return None  # If we are returning None we will use fallback

        return PaperInfo(
            title=link.title,
            link=link.link,
            abstract=paper.get("abstract"),
            tldr=(paper.get("tldr") or {}).get("text"),
            venue=paper.get("venue"),
            citation_count=paper.get("citationCount"),
            pdf_url=(paper.get("openAccessPdf") or {}).get("url"),
            source="semantic_scholar",
        )
    except Exception:
        return None


# ---------- first fallback ----------


def _fetch_from_publisher_page(link: LinkPage) -> Optional[PaperInfo]:
    """
    Scrape the publisher page directly and read its meta tags for the abstract.

    ---

    Args:
        link (str): the link you have.

    Returns:
        PaperInfo | None: the result we could get.
    """

    try:
        resp = requests.get(link.link, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        def get_meta(name):
            tag = soup.find("meta", attrs={"name": name})
            return tag["content"].strip() if tag and tag.get("content") else None

        abstract = get_meta("citation_abstract") or get_meta("description")
        if not abstract:
            return None

        return PaperInfo(
            title=link.title,
            link=link.link,
            abstract=abstract,
            pdf_url=get_meta("citation_pdf_url"),
            source="publisher_scrape",
        )
    except Exception:
        return None


# ---------- lastest fallback ----------


def _fetch_from_crossref(link: LinkPage) -> Optional[PaperInfo]:
    """
    Get article informations from Crossref API as the last fallback.

    ---

    Args:
        link (str): the link you have.

    Returns:
        PaperInfo | None: the result we could get.
    """

    try:
        resp = requests.get(
            "https://api.crossref.org/works",
            params={"query.bibliographic": link.title, "rows": 1},
            timeout=15,
        )
        items = resp.json().get("message", {}).get("items", [])
        if not items:
            return None

        item = items[0]
        abstract = item.get("abstract")
        if not abstract:
            return None

        abstract = BeautifulSoup(abstract, "html.parser").get_text(strip=True)

        return PaperInfo(
            title=link.title,
            link=link.link,
            abstract=abstract,
            venue=item.get("container-title", [None])[0],
            citation_count=item.get("is-referenced-by-count"),
            source="crossref",
        )
    except Exception:
        return None


# ---------- main chain ----------


def dedupe_links(links: List[LinkPage]) -> List[LinkPage]:
    """
    This function will filter us duplicated links.

    ---

    Args:
        links (List[LinkPage])

    Returns:
        List[LinkPage]
    """

    seen = set()
    unique_links = []

    for link in links:
        if link.link not in seen:
            seen.add(link.link)
            unique_links.append(link)

    return unique_links


def enrich_link(link: LinkPage) -> Optional[PaperInfo]:
    """
    This function will try all possibile ways that we could though to get papers informations.
    > **Note**: Use this function if you have only one link.

    ---

    Args:
        link (str): the link you have.

    Returns:
        PaperInfo | None: the result we could get.
    """

    for fetcher in (
        _fetch_from_arxiv,
        _fetch_from_semantic_scholar,
        _fetch_from_publisher_page,
        _fetch_from_crossref,
    ):
        result = fetcher(link)
        if result:
            return result

    # If none of them worked return none
    return None


def enrich_links(links: List[LinkPage]) -> List[PaperInfo]:
    """
    This function will try all possibile ways that we could though to get papers informations.
    > **Note**: Use this function if you have only more than one link.
    ---

    Args:
        link (str): the link you have.

    Returns:
        List[PaperInfo]: the result we could get.
    """

    linkPages = dedupe_links(links)
    paperInfos: list[PaperInfo] = []

    for link in linkPages:
        page = enrich_link(link)
        if page:
            paperInfos.append(page)

    return paperInfos
