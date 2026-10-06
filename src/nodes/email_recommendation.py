import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from configs import get_configs
from src.state import AgentState
from src.types import ChosenArticleStructure

import markdown
import json
import re
import logging

logger = logging.getLogger(__name__)


def _json_to_markdowns(chosen_articles: list[ChosenArticleStructure]):
    chosen_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    result = ""
    for article in chosen_articles:
        result += f"## {article.title}\n"
        result += f"- **relevance_score**: {article.relevance_score}\n"
        result += (
            f"- **technical_interest_score**: {article.technical_interest_score}\n"
        )
        result += f"- **confidence**: {article.confidence}\n"
        result += f"- **reason**: {article.reason}\n"
        result += f"- **key_evidence**: {article.key_evidence}\n"
        result += f"- **search_for**: {article.search_for}\n"
        result += f"- **direct_link**: {article.direct_link}\n"
        relevant_topics = " | ".join(article.relevant_topics)
        result += f"- **relevant_topics**: {relevant_topics}\n\n---\n\n"

    return result


def get_email_recomendation_node():
    """
    This function will return `email_recomendation_node` and this node will email user the previuse nodes response.
    """
    configs = get_configs()

    def email_recomendation_node(state: AgentState):
        recommendations = state.get("recommendations", [])
        if len(recommendations) == 0:
            logger.warning("from agent node we have got no recommendations!")
            return {}

        fields = ChosenArticleStructure.__dataclass_fields__
        chosen_articles: list[ChosenArticleStructure] = []
        for text in recommendations:
            text = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE
            ).strip()

            data = json.loads(text)

            chosen_articles.extend(
                ChosenArticleStructure(**{k: v for k, v in item.items() if k in fields})
                for item in data
            )

        body = markdown.markdown(
            _json_to_markdowns(chosen_articles=chosen_articles),
            extensions=["extra", "tables", "fenced_code"],
        )
        sender = configs.email
        password = configs.password
        subject = "Recommended Articles!"

        with open("latest.html", "w") as f:
            f.write(body)

        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = sender
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            logger.info("Sending email to %s.", sender)
            smtp.login(sender, password)
            smtp.send_message(msg)

    return email_recomendation_node
