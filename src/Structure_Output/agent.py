from google.adk.agents import LlmAgent
from google.adk.tools import google_search, AgentTool
from pydantic import BaseModel, Field

# 1. Define the Data Structure
# This is what the Root Agent will use to format its final answer.
class Capital(BaseModel):
    capital: str = Field(description="The name of the capital city")
    popultaion: int = Field(description="The population of the capital city")


root_agent = LlmAgent(
    name="Structure_Output",
    model="gemini-2.5-flash-lite",
    description="You are a helpful assistant that generates the capital of a country and its population.",
    instruction="""
    You are a helpful assistant that generates the capital of a country and its population.
    GUIDLINES : 
    IF the user ask for a country , you will use your general knowledge to answer then give its population.
    IF the user ask for a country not in the world , you will say country null and population is null  , you will use your general knowledge to answer then give its population.
    IMPORTANT: Your response MUST be valid JSON matching this structure:
        {
            "capital": "Capital of the country",
            "popultaion": Population of the country in numbers,
        }

        DO NOT include any explanations or additional text outside the JSON response.
    """,
    output_schema=Capital,
    output_key="Capital_of_country"
)