import os
from dotenv import load_dotenv


class Configs:
    is_development: bool = True
    use_proxy: bool = True
    proxy_link: str = "none"
    tool_calls_count: int = 5

    groq_llm_name: str = "openai/gpt-oss-20b"
    google_llm_name: str = "openai/gpt-oss-20b"
    openouter_llm_name: str = "openai/gpt-oss-20b"

    email: str = "none"
    password: str = "none"

    groq_apikey: str = ""
    tavily_apikey: str = ""


_configs = None


def get_configs():
    global _configs

    if _configs is None:
        load_dotenv()

        configs = Configs()
        configs.is_development = os.getenv("DEVELOPMENT", "true").lower() == "true"
        configs.use_proxy = os.getenv("USE_PROXY", "true").lower() == "true"
        configs.proxy_link = os.getenv("PROXY_LINK", configs.proxy_link)
        configs.tool_calls_count = int(
            os.getenv("TOOL_CALLS_COUNT", configs.tool_calls_count)
        )

        configs.groq_llm_name = os.getenv("GROQ_LLM_NAME", configs.groq_llm_name)
        configs.google_llm_name = os.getenv("GOOGLE_LLM_NAME", configs.google_llm_name)
        configs.openouter_llm_name = os.getenv(
            "OPENROUTER_LLM_NAME", configs.groq_llm_name
        )

        configs.groq_apikey = os.getenv("GROQ_KEY", configs.groq_apikey)
        configs.tavily_apikey = os.getenv("TAVILY_API_KEY", configs.tavily_apikey)

        configs.email = os.getenv("EMAIL", configs.email)
        configs.password = os.getenv("EMAIL_PASSWORD", configs.password)

        _configs = configs

        return _configs
    else:
        return _configs
