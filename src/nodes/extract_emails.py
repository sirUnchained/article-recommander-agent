from configs import get_configs
from src.types import EmailPage
from src.state import AgentState

from email.header import decode_header
import email as email_lib

import imaplib
import logging

logger = logging.getLogger(__name__)


SENDER_FILTERS = [
    "scholaralerts-noreply@google.com",
    "daily_papers_digest@notifications.huggingface.co",
    "top ai papers of the week <newsletters-noreply@linkedin.com>",
    "arxiv.org",
]


def _matches_filter(sender, sender_filters):
    """
    This function will filter senders, if the sender already exists in filters we return `True` else `False`.
    """
    sender = (sender or "").lower()

    for f in sender_filters:
        from_ok = f in sender
        if from_ok:
            return True
    return False


def _checking_email():
    """
    This function will connect to your email using the email and passkey (as password).
    """
    email = get_configs().email
    password = get_configs().password

    imap_url = "imap.gmail.com"

    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(email, password)
        mail.select("inbox")
        return mail
    except Exception as e:
        logger.error("Connection to email failed: %s", e)
        raise


def get_email_extractor_node(limit=50):
    """
    This function will return `email_extractor_node` which is used to search input emails, find specifice ones
    and then keep them all in single array, finally we send the, to next node.
    """

    mail = _checking_email()

    def email_extractor_node(state: AgentState):
        """
        Return a list of dicts with subject, sender, and body for unread emails.

        ---

        Args:
            mail (IMAP4_SSL): An instance of imaplib used for emails.
            limit (int): Limit of emails to cheack.

        Returns:
            results (list[EmailPage]):
                each element of this list contains `id`, `subject`, `from`, `body`.
        """

        # fetch `unseen` emails
        status, messages = mail.search(None, "UNSEEN")

        if status != "OK":
            logger.error("searching in email just failed: %s", status)
            return {"emails": []}

        email_ids = messages[0].split()
        results = []

        # loop email ids
        for eid in email_ids[-limit:]:
            # fetching emails and check if they are ok.
            # note: "(BODY.PEEK[])" means read them but dont seen them
            status, msg_data = mail.fetch(eid, "(BODY.PEEK[])")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]  # type: ignore
            msg = email_lib.message_from_bytes(raw_email)  # type: ignore

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            sender = msg.get("From")

            # filtering each email with their sender
            if not _matches_filter(sender, SENDER_FILTERS):
                continue

            # reading body and saving it
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in disposition:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            results.append(
                EmailPage(
                    id=eid.decode(),
                    subject=subject,
                    sender=sender,
                    body=body.strip(),
                )
            )

        logger.info("found %d emails as result", len(results))
        return {"emails": results, "papers_limit": 3}

    return email_extractor_node
