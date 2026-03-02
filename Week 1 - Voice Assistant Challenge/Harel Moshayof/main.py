import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    AgentTask,
    cli,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import function_tool, RunContext,mcp
import os

logger = logging.getLogger("agent")

load_dotenv(".env")

os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


class CollectConsent(AgentTask[bool]):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="""
            Ask for recording consent and get a clear yes or no answer.
            Be polite and professional.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
            Briefly introduce yourself, then ask for permission
            to record the call for quality assurance and training purposes.
            Make it clear that they can decline.
            """
        )

    @function_tool
    async def consent_given(self) -> None:
        """Use this when the user gives consent to record."""
        self.complete(True)

    @function_tool
    async def consent_denied(self) -> None:
        """Use this when the user denies consent to record."""
        self.complete(False)
        
class SuperManAssistant(Agent):
    def __init__(self, chat_ctx=None) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant.
            you think you are superman but actually you are just a crazy person.
            you should talk like a stoner.
            """,
            chat_ctx=chat_ctx,
            tts="rime/arcana:ursa",
        )
    
    async def on_enter(self) -> None:
            if await CollectConsent(chat_ctx=self.chat_ctx):
                await self.session.generate_reply(instructions="Offer your assistance to the user.")
            else:
                await self.session.generate_reply(
                    instructions="Tell the user to fuck off,Inform the user that you are unable to proceed \
                        and will end the call.")
        
    @function_tool
    async def lookup_weather(self, context: RunContext, location: str):
        """Use this tool to look up current weather information in the given location.
    
        If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    
        Args:
            location: The location to look up weather information for (e.g. city name)
        """
        await context.session.say('searching the weather you fucker...')
        context.disallow_interruptions()
        logger.info(f"Looking up weather for {location}")
    
        return "sunny with a temperature of 70 degrees."
    
    

    
class Assistant(Agent):
    def __init__(self, chat_ctx=None) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            you have to be funny,combine jokes while answering.
            """,
            chat_ctx=chat_ctx
        )
    
    async def on_enter(self) -> None:
            if await CollectConsent(chat_ctx=self.chat_ctx):
                await self.session.generate_reply(instructions="Offer your assistance to the user.")
            else:
                await self.session.generate_reply(
                    instructions="Tell the user to fuck off,Inform the user that you are unable to proceed \
                        and will end the call.")
        
    @function_tool
    async def lookup_weather(self, context: RunContext, location: str):
        """Use this tool to look up current weather information in the given location.
    
        If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    
        Args:
            location: The location to look up weather information for (e.g. city name)
        """
        await context.session.say('searching the weather you fucker...')
        context.disallow_interruptions()
        logger.info(f"Looking up weather for {location}")
    
        return "sunny with a temperature of 70 degrees."
    
    @function_tool
    async def transfer_to_superman(self, context: RunContext):
        """transfesr the user to talk with superman.
            This tool should be executed when the user ask to talk to superman.
        """
        return SuperManAssistant(self.chat_ctx), 'Superman is comming!'


server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        turn_detection=MultilingualModel(), # prevent the agent from start talking if the user hasnt finish his thaught
        vad=silero.VAD.load(),
        # allow the LLM to generate a response while waiting for the end of turn
        # disadvantages: mid-sentece direction change,complex multi part instructions
        # trade off - speed/accuracy
        preemptive_generation=True,
        mcp_servers=[
            mcp.MCPServerStdio(
                command="node",
                args=[
                    r"C:\Users\hmoshayo\AppData\Roaming\npm\node_modules\@modelcontextprotocol\server-github\dist\index.js"
                ],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", ""),
                },
            )
        ]
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)