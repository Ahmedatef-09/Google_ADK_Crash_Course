from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent
from google.adk.tools import google_search
import datetime

def get_current_time() -> dict:
    
    return {"time": datetime.datetime.now().strftime("%H:%M")}

root_agent = LlmAgent(
    name="Tool_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.5-flash-lite",
    description="Tool agent",
    instruction="""
    You are a helpful assistant that uses tools to answer the user's question.
    Rules : 
    - If user asks about current date, time, use get_current_time tool then respond to the user 
    """,
    tools=[get_current_time]
)

