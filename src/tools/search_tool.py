from langchain_tavily import TavilySearch


def get_tavily_search_tool():
    return TavilySearch(max_results=3, handle_tool_error=True, topic="general")
