from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import AgentState
from src.agents import researcher_agent, compliance_agent

# --- Persistence ---
memory = SqliteSaver.from_conn_string("checkpoints.sqlite3")

# --- Node Definitions ---

def researcher_node(state: AgentState):
    """Node for the LeadResearcherAgent."""
    result = researcher_agent.invoke(state)
    # We use HumanMessage to clearly attribute the output to the agent
    return {"messages": [HumanMessage(content=result["messages"][-1].content, name="LeadResearcher")]}

def compliance_node(state: AgentState):
    """Node for the EthicalComplianceSentinelAgent."""
    result = compliance_agent.invoke(state)
    return {"messages": [HumanMessage(content=result["messages"][-1].content, name="EthicalComplianceSentinel")]}

# This is a placeholder node for the human review step
def human_review_node(state: AgentState):
    """A node that simply passes the state through, acting as a break point."""
    return {}

# --- Supervisor and Edge Logic ---

def supervisor_router(state: AgentState) -> str:
    """
    This is the supervisor agent (OperationalExecutiveAgent).
    It routes tasks to the appropriate worker agent, requests human review, or ends the process.
    """
    print(f"---[Supervisor Called | Last Sender: {state['sender']}]---")
    last_message = state["messages"][-1]

    if last_message.name == "LeadResearcher":
        print("Supervisor: Routing to Compliance for review.")
        return "EthicalComplianceSentinel"

    elif last_message.name == "EthicalComplianceSentinel":
        print("Supervisor: Routing to 'HAZE' for human review.")
        return "human_review" # This triggers the interrupt

    elif last_message.name == "human_review":
        print("Supervisor: Human review complete. Ending workflow.")
        return "END"

    else: # Initial call
        print("Supervisor: Routing to Researcher.")
        return "LeadResearcher"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("LeadResearcher", researcher_node)
workflow.add_node("EthicalComplianceSentinel", compliance_node)
workflow.add_node("human_review", human_review_node)

# Set the entrypoint
workflow.set_entry_point("LeadResearcher")

# Add the conditional edges from the supervisor logic
workflow.add_conditional_edges(
    "LeadResearcher",
    supervisor_router,
    {"EthicalComplianceSentinel": "EthicalComplianceSentinel"}
)
workflow.add_conditional_edges(
    "EthicalComplianceSentinel",
    supervisor_router,
    {"human_review": "human_review"}
)
workflow.add_conditional_edges(
    "human_review",
    supervisor_router,
    {"END": END}
)

# Compile the graph with persistence and the HITL interrupt
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"] # This pauses the graph BEFORE the human_review node runs
)

print("Graph compiled successfully with persistence and HITL.")