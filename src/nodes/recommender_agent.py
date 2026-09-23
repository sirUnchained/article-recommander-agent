from langchain.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate

from langchain.agents import create_agent

from src.state import AgentState
from src.prompts import get_system_prompt
from src.tools.search_tool import get_tavily_search_tool

import logging

logger = logging.getLogger(__name__)


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
        papers = state.get("papers", [])
        papers_limit = state.get("papers_limit", 5)
        recommendations: list[str] = []

        # In this loop, until we did not reach the limit we just create article string and then
        # append it to articles, after we reach the limit we will start calling llm.
        articles = ""
        for i in range(len(papers)):
            if i % papers_limit != 0:
                article = f"# Article {i+1}\n\n"
                article += f"## Title\n\n{papers[i].title}\n\n"
                article += f"## Abstract\n\n{papers[i].abstract}\n\n"
                article += f"## Link to Site\n\n{papers[i].link}\n\n"
                article += f"## PDF url\n\n{papers[i].pdf_url}\n\n"
                articles += article
            else:
                # If an llm failed in the list, we'll log it and try other agents
                for i, agent in enumerate(agents):
                    try:
                        response = agent.invoke({"messages": [("user", articles)]})
                        recommendations.append(
                            response.get(
                                "text",
                                "there is no text here, check me in recomender_agent.py file!",
                            )
                        )

                        break  # no error? skip agents loop
                    except Exception as e:
                        logger.warning(
                            "Agent number %d failed to run, continue with next agent, error: %s",
                            i + 1,
                            e,
                        )
                # And if all agents failed and we have no recommandation
                else:
                    logger.warning("All agents were tried but none of them worked")
                    recommendations.append(
                        "# There is an error in calling agents! please fix it"
                    )

                articles = ""

        return {"recommendations": recommendations}

    return recommender_node
