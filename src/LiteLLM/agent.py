from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent ,LlmAgent
from google.adk.tools import google_search
import datetime

def get_current_time() -> dict:
    
    return {"time": datetime.datetime.now().strftime("%H:%M")}

def get_current_name() -> dict:
    
    return {"name": "LiteLLM"}

from google.adk.models.lite_llm import LiteLlm
MODEL_GPT_4O = "openai/gpt-4o"
root_agent = LlmAgent(
    name="LiteLLM",
    # https://ai.google.dev/gemini-api/docs/models
    model=LiteLlm(model=MODEL_GPT_4O),
    description="Tool agent",
    instruction="""
    You are a helpful assistant that uses tools to answer the user's question.
    Rules : 
    - Reply to the user using get_current_time tool if he asks about time 
    - Reply to the user using get_current_name tool if he asks about name 
   """,
    tools=[get_current_time, get_current_name]
)
