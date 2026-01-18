import os
import asyncio

from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    JobProcess,
    AgentSession,
    Agent,
)
from livekit.plugins import deepgram, silero, cartesia, openai

from dotenv import load_dotenv

load_dotenv()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.environ.get("CEREBRAS_API_KEY"),
            model="llama3.1-8b",
        ),
        tts=cartesia.TTS(voice="79693aee-1207-4771-a01e-20c393c89e6f", language="it"),
    )

    agent = Agent(
        instructions="Sei un assistente vocale. Comportati come se stessimo avendo una conversazione umana, senza formattazione speciale o intestazioni, solo linguaggio naturale. Rispondi sempre in italiano."
    )

    await ctx.connect()
    await session.start(room=ctx.room, agent=agent)
    await asyncio.sleep(1)
    await session.say("Ciao, come posso aiutarti oggi?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))