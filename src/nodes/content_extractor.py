from helpers.link_extractors import extract_paper_links
from helpers.pageinfo_extractor import enrich_links
from src.state import AgentState
from src.types import EmailPage

import logging

logger = logging.getLogger(__name__)


def get_content_extractor_node():
    """
    This function will return `content_extractor_node` adn this node is used to extract information from papers which will be send to next node.
    """

    def content_extractor_node(state: AgentState):
        emails: list[EmailPage] = state.get("emails", [])
        if len(emails) == 0:
            logger.warning("There is no email so we can extract no paper link.")
            return

        links = extract_paper_links(emails)
        if len(links) == 0:
            logger.warning("In the emails we did not found any links.")
            return

        logger.info("We extracted %d links from papers.", len(links))

        papersInfo = enrich_links(links=links)

        return {"papers": papersInfo, "papers_limit": 10}

    return content_extractor_node
