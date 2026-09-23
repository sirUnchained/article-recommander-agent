from src.graph import build_graph


def chat_with_agent():
    graph = build_graph()

    return graph.invoke(input={})

if __name__ == '__main__':
    graph.invoke(input={})
