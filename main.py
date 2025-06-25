from agents import Agent, agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, RunConfig
import os
from dotenv import load_dotenv
import chainlit as cl
from openai.types.responses import  ResponseTextDeltaEvent

load_dotenv()

gemini_api_key = os.getenv("Gemini_Api_key")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

agent = Agent(
    name="Frontend Expert",
    instructions="You are a frontend expert"
)

@cl.on_chat_start
async def handle_Start():
    cl.user_session.set("history", [])
    await cl.Message(content= "Hello this is asfa how can I help you!").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})
    content = history
   
#  process the message here

    msg = cl.Message(content= "")
    await msg.send()

    result =  Runner.run_streamed(
        agent,
        input=content,
        run_config=config
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    await cl.Message(content=result.final_output).send()