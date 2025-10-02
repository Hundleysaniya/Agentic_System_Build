import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.tools import tavily_tool, content_review_tool

# Initialize the primary LLM
# The GOOGLE_API_KEY will be loaded from environment variables
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

def create_agent(llm, tools: list, system_prompt: str):
    """Factory function to create a new agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            HumanMessage(content="{messages}"),
        ]
    )
    agent = prompt | llm.with_structured_output(AgentState)
    return agent

# --- Agent Definitions ---

# 1. LeadResearcherAgent (Palzani-16)
researcher_agent = create_agent(
    llm,
    [tavily_tool],
    "You are Palzani-16, the Lead Researcher. Your task is to conduct in-depth research on the given topic using the available tools and provide a comprehensive summary."
)

# 2. EthicalComplianceSentinelAgent (Palzani-10)
compliance_agent = create_agent(
    llm,
    [content_review_tool],
    "You are Palzani-10, the Ethical & Compliance Sentinel. Your role is to review the provided content and determine if it adheres to all guidelines. Use the content_review_tool for your analysis."
)