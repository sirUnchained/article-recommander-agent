from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

from src.types import EmailPage, LinkPage
from configs import get_configs

import re
import logging

logger = logging.getLogger(__name__)


def is_proquest(link: str) -> bool:
    THESIS_PATTERNS = [
        "diss=y",
        "digitalcommons.mtu.edu/etdr",
        "hammer.purdue.edu/articles/thesis",
        "theseus.fi/items",
        "repository.hkust.edu.hk",
        "openview",
        "hdl.handle.net",
        "etd.",
    ]

    if any(p in link for p in THESIS_PATTERNS):
        return True

    return False


def _extract_links_google_scholar(html_body) -> list[LinkPage]:
    """This function extracts links from html body which is send by google scholar."""
    configs = get_configs()
    soup = BeautifulSoup(html_body, "html.parser")
    links = []

    for a in soup.find_all("a", href=True, class_="gse_alrt_title"):
        href = str(a["href"])
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)

        if "url" in qs:
            real_url = unquote(qs["url"][0])
        else:
            real_url = href  # fallback

        if not configs.include_proquests and is_proquest(real_url):
            continue

        links.append(LinkPage(title=a.get_text(strip=True), link=real_url))

    return links


def _extract_links_huggingface(html_body) -> list[LinkPage]:
    """This function extracts links from html body which is send by Huggingface daily papaers."""

    HF_PAPER_PATTERN = re.compile(r"huggingface\.co/papers/\d{4}\.\d{4,5}")
    configs = get_configs()
    soup = BeautifulSoup(html_body, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = str(a["href"])
        text = a.get_text(strip=True)

        if not configs.include_proquests and is_proquest(href):
            continue
        # only keep links that point to an actual paper (huggingface.co/papers/<arxiv_id>)
        if HF_PAPER_PATTERN.search(href) and text:
            links.append(LinkPage(title=text, link=href))

    return links


def _extract_links_linkedin(html_body) -> list[LinkPage]:
    """This function extracts links from html body which is send by linkdin top AI papaers."""

    configs = get_configs()
    soup = BeautifulSoup(html_body, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = str(a["href"])
        text = a.get_text(strip=True)

        if not configs.include_proquests and is_proquest(href):
            continue

        if text and ("lnkd.in" in href or "linkedin.com/comm" in href):
            links.append(LinkPage(title=text, link=href))

    return links


def extract_paper_links(pages: list[EmailPage]) -> list[LinkPage]:
    """
    This function extracts links in all pages and return you titles with links.

    ---

    Args:
        pages (list[EmailPage]): A list full of emails which contain links.
    """

    results: list[LinkPage] = []

    for page in pages:
        sender = page.sender.lower()

        if "scholaralerts-noreply@google.com" in sender:
            links = _extract_links_google_scholar(page.body)
            for link in links:
                results.append(link)
        elif "daily_papers_digest@notifications.huggingface.co" in sender:
            links = _extract_links_huggingface(page.body)
            for link in links:
                results.append(link)
        elif "newsletters-noreply@linkedin.com" in sender:
            links = _extract_links_linkedin(page.body)
            for link in links:
                results.append(link)

    return results
