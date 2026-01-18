
from .agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
import asyncio
from google.adk.events import Event, EventActions
import time

session_service = InMemorySessionService()
state_context = {
    "user_name": "Atef",
    "user_post_preferences": """
        - LinkedIn: Professional, engaging, and relevant to the topic.
            should have a primary hook, not more than 60 characters.
            should have a line break after the hook.
            should have a post-hook that is either supporting the hook or completely inverse of the hook to grab attention.
            should be in a conversational tone and should be easy to read.
            should have bullet points in the post to make it easy to read.
            should have actionable items in the post to make it easy to follow.
            should have a question to engage the audience.
            should ask the audience to share their thoughts in the comments. And to repost.
            should use emojis to make the post more engaging.
            should use hashtags to make the post more discoverable.
        - Instagram: Engaging, fast paced, and relevant to the topic.
            should have a primary hook, which grabs the attention of the audience.
            should have a call to action at the end.
        """,
}

SESSION_ID = str(uuid.uuid4())
USER_ID = "atef"
APP_NAME = "post_generator"
print("1")

async def main():   
    session = await session_service.create_session(
        session_id=SESSION_ID,
        user_id=USER_ID,
        app_name=APP_NAME,
        state = state_context,
    )       
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )


    print("Agent: Hello! I am your Assistant. How can I help you with your post today?")
    user_text = input("You: ") 
    user_input = types.Content(
        role="user",
        parts=[types.Part(text=user_text)],    
    )   

    async for event in runner.run_async(
        new_message=user_input,
        user_id=USER_ID,
        session_id=SESSION_ID,
    ):
       
        
        if event.is_final_response:
            if event.content and event.content.parts:
                print (f"event_content : {event}")
                #breakpoint()
                print("Final response:",event.content.parts[0].text)


                
                

    session = await session_service.get_session(
        session_id=SESSION_ID,
        user_id=USER_ID,
        app_name=APP_NAME,
    )
    print("usage:",event.usage_metadata.total_token_count)
    for key, value in session.state.items():
        print(f'{key}: {value}')

# 4. Entry point to run the async function
if __name__ == "__main__":
    asyncio.run(main())