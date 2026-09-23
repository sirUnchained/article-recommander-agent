from fastapi import FastAPI
from dotenv import load_dotenv

from src.chat import chat_with_agent
from configs import get_configs

import os
import logging

# ========== logger and configs ============
logger = logging.getLogger(__name__)
load_dotenv()
configs = get_configs()

if configs.use_proxy:
    logger.info("Proxy enabled.")
    os.environ["HTTP_PROXY"] = configs.proxy_link
    os.environ["HTTPS_PROXY"] = configs.proxy_link

# =========== app and routes ==========
app = FastAPI()


@app.get("/health")
def check_health():

    return "All ok!"


@app.get("/check-email")
def check_articles():

    chat_with_agent()

    return "You may recive an email soon."
