from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent


root_agent = LlmAgent(
    name="Basic_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.5-flash-lite",
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user. 
    Ask for the user's name and greet them by name.
    """
)