import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from configs import get_configs
from src.state import AgentState

import markdown
import logging

logger = logging.getLogger(__name__)


def _markdowns_to_html(recommendations: list[str]) -> str:
    recommendation = ""

    for rec in recommendations:
        recommendations += markdown.markdown(rec)

    return recommendation


def get_email_recomendation_node():
    """
    This function will return `email_recomendation_node` and this node will email user the previuse nodes response.
    """
    configs = get_configs()

    def email_recomendation_node(state: AgentState):
        recommendations = state.get("recommendations", [])
        if len(recommendations) == 0:
            return

        body = _markdowns_to_html(recommendations)
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
