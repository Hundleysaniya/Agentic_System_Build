from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Represents the shared state of the agentic system.

    Attributes:
        messages: The list of messages that have been exchanged.
        sender: The name of the last agent to modify the state.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str