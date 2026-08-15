from langgraph.graph import StateGraph, START, END
from langchain_core.messages import (
    BaseMessage,
    SystemMessage
)
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
import sqlite3
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated

from dotenv import load_dotenv

from .tools import TOOLS
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

from .prompt import SYSTEM_PROMPT
from .schemas import IssueOutput

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


load_dotenv()


# ==================================================
# STATE
# ==================================================

class Chat(TypedDict, total=False):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

    report_mode: bool

    issue_category: str
    issue_weight: float
    estimated_cost_range: str
    issue_description: str

    reporter_name: str
    reporter_phone: str

    issue_location: dict | None
    evidence: str | None

    report_confirmed: bool


# ==================================================
# LLM
# ==================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7
)


# ==================================================
# TOOLS
# ==================================================

tools = TOOLS

tool_node = ToolNode(tools)

llm_with_tools = llm.bind_tools(tools)


# ==================================================
# NORMAL / ISSUE CHAT NODE
# ==================================================

def chatnode(state: Chat):

    messages = state["messages"]

    messages_with_system = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        *messages
    ]

    response = llm_with_tools.invoke(
        messages_with_system
    )

    return {
        "messages": [response]
    }


# ==================================================
# TOOL RESULT / CONTINUE CONVERSATION
# ==================================================

def tools_node(state: Chat):

    return state


# ==================================================
# MEMORY
# ==================================================

conn = sqlite3.connect(
    "chatbot_memory.db",
    check_same_thread=False
)

memory = SqliteSaver(conn)


# ==================================================
# GRAPH
# ==================================================

workflow = StateGraph(Chat)


workflow.add_node(
    "chat_node",
    chatnode
)

workflow.add_node(
    "tools",
    tool_node
)


# ==================================================
# START
# ==================================================

workflow.add_edge(
    START,
    "chat_node"
)


# ==================================================
# CHAT → TOOL OR END
# ==================================================

workflow.add_conditional_edges(
    "chat_node",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)


# ==================================================
# TOOL → CHAT
# ==================================================

workflow.add_edge(
    "tools",
    "chat_node"
)


# ==================================================
# COMPILE
# ==================================================

chatbot = workflow.compile(
    checkpointer=memory
)