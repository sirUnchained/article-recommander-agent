from fastapi import FastAPI
from dotenv import load_dotenv

from src.chat import chat_with_agent


import logging

logger = logging.getLogger(__name__)


app = FastAPI()
load_dotenv()


@app.get("/health")
def check_health():

    return "All ok!"


@app.get("/check-email")
def check_articles():

    chat_with_agent()

    return "You may recive an email soon."
