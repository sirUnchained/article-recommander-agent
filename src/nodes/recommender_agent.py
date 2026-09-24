from langchain.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate

from langchain.agents import create_agent

from src.state import AgentState
from src.prompts import get_system_prompt
from src.tools.search_tool import get_tavily_search_tool

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


def _call_agents(batch_of_artciles: str, agents: list[CompiledStateGraph]):
    for i, agent in enumerate(agents):
        try:
            response = agent.invoke({"messages": [("user", batch_of_artciles)]})
            return response.get(
                "text",
                "there is no text here, check me in recomender_agent.py file!",
            )

        except Exception as e:
            logger.warning(
                "Agent number %d failed to run, continue with next agent, error: %s",
                i + 1,
                e,
            )

    logger.warning("All agents were tried but none of them worked")
    return "# There is an error in calling agents! please fix it"


def _create_batches_of_articles(articles, articles_limit):
    """
    This fucntion will get all of articles with a limit, with the limit it choses some articles
    and turn them into a single batch (prompt), this process will be repeated until we have turned
    all articles into a batch.
    """
    current = ""
    batch_of_articles: list[str] = []

    for i, paper in enumerate(articles):
        article = f"# Article {i + 1}\n\n"
        article += f"## Title\n\n{paper.title}\n\n"
        article += f"## Abstract\n\n{paper.abstract}\n\n"
        article += f"## Link to Site\n\n{paper.link}\n\n"
        article += f"## PDF url\n\n{paper.pdf_url}\n\n"
        current += article

        if (i + 1) % articles_limit == 0:
            batch_of_articles.append(current)
            current = ""

    if current:
        batch_of_articles.append(current)

    return batch_of_articles


def get_recommender_node(llms_no_tool: list[BaseChatModel]):
    """
    This function will return a recommender node, the recommender node will create
    a list of agents which work together to recommend aricles.

    ---

    Args:
        llms_no_tool (list[BaseChatModel]):
            This is list of llms, we will bind tools and system prompt later.
    """

    agents: list[CompiledStateGraph] = []
    system_prompt: str = get_system_prompt()
    search_tools = get_tavily_search_tool()

    # creating an array of agents which have tools + system prompt + llm
    for llm in llms_no_tool:
        agents.append(
            create_agent(llm, tools=[search_tools], system_prompt=system_prompt)
        )

    def recommender_node(state: AgentState):
        articles = state.get("articles", [])
        articles_limit = state.get("articles_limit", 3)
        recommendations: list[str] = []

        batches_of_articles = _create_batches_of_articles(
            articles=articles, articles_limit=articles_limit
        )

        # we are calling agent using concurency, we pass each one a single batch of articles.
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_index = {
                executor.submit(_call_agents, batch, agents): i
                for i, batch in enumerate(batches_of_articles)
            }

            for future in as_completed(future_to_index):
                recommendations.append(future.result())

        return {"recommendations": recommendations}

    return recommender_node
