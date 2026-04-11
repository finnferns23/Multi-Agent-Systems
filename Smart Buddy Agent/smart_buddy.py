# Import necessary dependencies
import os
import logging
from typing import TypedDict, Annotated, List, Callable
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# INITIAL SETUP & LOGGING
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[SmartBuddy] %(asctime)s — %(levelname)s — %(message)s",
)

logger = logging.getLogger(__name__)

# Validate environment variables
if not os.environ.get("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY missing in .env file.")
    raise ValueError("OPENAI_API_KEY missing.")

if not os.environ.get("TAVILY_API_KEY"):
    logger.error("TAVILY_API_KEY missing in .env file.")
    raise ValueError("TAVILY_API_KEY missing.")


# TOOL DEFINITIONS
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def web_search(query: str):
    """
    Search the web using Tavily.

    Parameters:
        query (str): Search query.

    Returns:
        list: Top results from Tavily Search API.
    """
    logger.info(f"Running web_search tool | Query='{query}'")

    if not query or len(query.strip()) == 0:
        return [{"error": "Empty query provided to web_search."}]

    try:
        return tavily.search(query=query, search_depth="basic")["results"]
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return [{"error": f"Tavily search failed: {str(e)}"}]


@tool
def calculator(a: float, b: float, operation: str):
    """
    Basic calculator tool supporting add/subtract/multiply/divide.

    Parameters:
        a (float): First number
        b (float): Second number
        operation (str): Operation type ("add", "subtract", "multiply", "divide")

    Returns:
        float | str: Result or error message
    """
    logger.info(f"Running calculator tool | {a} {operation} {b}")

# Validate inputs
    try:
        a = float(a)
        b = float(b)
    except Exception:
        return "Calculator error: Inputs must be numeric."

    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            return "Calculator error: Division by zero is not allowed."
        return a / b

    return "Calculator error: Unsupported operation."


# Register tools
toolbox: List[Callable] = [web_search, calculator]


# LLM SETUP
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(toolbox)


# GRAPH STATE (MEMORY)
class AgentState(TypedDict):
    """
    Represents the state held during graph execution.
    Stores a running history of messages in the conversation.
    """
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


# GRAPH NODES
def agent_node(state: AgentState):
    """
    The main agent node: decides whether to respond or call a tool.
    """
    logger.info("Agent thinking...")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(toolbox)


# CONDITIONAL BRANCHING LOGIC
def should_continue(state: AgentState):
    """
    Determines whether the agent should call a tool or end.

    Returns:
        str: "run_tool" or "end"
    """
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.info("Decision: Run tool")
        return "run_tool"

    logger.info("Decision: End")
    return "end"


# BUILD GRAPH
graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("run_tool", tool_node)

graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"run_tool": "run_tool", "end": END},
)

graph_builder.add_edge("run_tool", "agent")

smart_study_buddy = graph_builder.compile()


# RUNTIME EXECUTION WRAPPER
def run_agent(question: str):
    """
    Run the Smart Study Buddy agent on a given question.

    Parameters:
        question (str): User-provided question.

    Returns:
        None (prints result)
    """
    logger.info(f"Received user question: {question}")

    inputs = {"messages": [HumanMessage(content=question)]}

    final_answer = None

    for event in smart_study_buddy.stream(inputs, stream_mode="values"):
        msg = event["messages"][-1]

        if isinstance(msg, AIMessage) and not msg.tool_calls:
            final_answer = msg.content

    if final_answer:
        print("\n🎓 Smart Buddy Answer:", final_answer)
    else:
        print("\n⚠️ Smart Buddy couldn't generate a final response.")


# SAMPLE TESTS (Safe to remove in production)
if __name__ == "__main__":
    run_agent("What will be the result of multiplying 345 by 5?")
    run_agent("Who is the current President of India?")
