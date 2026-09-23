from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter

from langgraph.graph import StateGraph
from langgraph.constants import START, END

from src.state import AgentState
from src.nodes.extract_emails import get_email_extractor_node
from src.nodes.content_extractor import get_content_extractor_node
from src.nodes.recommender_agent import get_recommender_node
from src.nodes.email_recommendation import get_email_recomendation_node

import logging

logger = logging.getLogger(__name__)


def build_graph():
    openrouter = ChatOpenRouter(
        model="nvidia/nemotron-3-ultra-550b-a55b:free", temperature=0.5
    )
    groq = ChatGroq(model="openai/gpt-oss-20b", temperature=0.5)
    google = ChatGoogleGenerativeAI(model="", temperature=0.5)

    # call functions to create nodes

    email_extractor_node = get_email_extractor_node()
    content_extractor_node = get_content_extractor_node()
    recommender_node = get_recommender_node(llms_no_tool=[google, openrouter, groq])
    email_recomendation_node = get_email_recomendation_node()

    # build graph space
    graph_builder = StateGraph(AgentState)

    # insert nodes to graph space
    graph_builder.add_node(node=email_extractor_node)
    graph_builder.add_node(node=content_extractor_node)
    graph_builder.add_node(node=recommender_node)
    graph_builder.add_node(node=email_recomendation_node)

    # insert edges
    graph_builder.add_edge(start_key=START, end_key=email_extractor_node.__name__)
    graph_builder.add_edge(
        start_key=email_extractor_node.__name__, end_key=content_extractor_node.__name__
    )
    graph_builder.add_edge(
        start_key=content_extractor_node.__name__, end_key=recommender_node.__name__
    )
    graph_builder.add_edge(
        start_key=recommender_node.__name__, end_key=email_recomendation_node.__name__
    )
    graph_builder.add_edge(start_key=email_recomendation_node.__name__, end_key=END)

    # compile the graph
    graph = graph_builder.compile()
    logger.info("graph compiled with no error")

    return graph
