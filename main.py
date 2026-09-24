from fastapi import FastAPI
from dotenv import load_dotenv

from src.chat import chat_with_agent
from configs import get_configs

import os
import logging

# ========== logger and configs ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
configs = get_configs()

if configs.use_proxy:
    logger.info("Proxy enabled.")
    os.environ["http_proxy"] = configs.proxy_link
    os.environ["https_proxy"] = configs.proxy_link

# =========== app and routes ==========
app = FastAPI()


@app.get("/health")
def check_health():

    return {"status": 200, "message": "All ok!"}


@app.get("/check-email")
def check_articles():

    chat_with_agent()

    return {"status": 200, "message": "You may recive an email soon."}


if __name__ == "__main__":
    chat_with_agent()
