from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google
from livekit.plugins import noise_cancellation
from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS
from tools import (
    search_web, 
    get_current_time, 
    calculate_math, 
    get_weather_info, 
    create_reminder, 
    get_system_info, 
    translate_text,
    generate_password,
    manage_memory,
    url_shortener,
    qr_code_generator,
    text_analyzer,
    ai_assistant,
    code_analyzer,
    explain_concept,
    creative_writing,
    data_insights
)
from livekit.plugins import openai

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",
                temperature=0.8,
                instructions=AGENT_INSTRUCTIONS,
            ),
            tools=[
                search_web,
                get_current_time,
                calculate_math,
                get_weather_info,
                create_reminder,
                get_system_info,
                translate_text,
                generate_password,
                manage_memory,
                url_shortener,
                qr_code_generator,
                text_analyzer,
                ai_assistant,
                code_analyzer,
                explain_concept,
                creative_writing,
                data_insights
            ],
        )
        


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=SESSION_INSTRUCTIONS
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))