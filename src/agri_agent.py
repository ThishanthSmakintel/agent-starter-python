import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
)
from livekit.plugins import silero
import boto3
import json

logger = logging.getLogger("agri-agent")
load_dotenv(".env.local")

# AWS Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class AGRIAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are AGRI, an AI agricultural assistant for Sri Lankan farmers.
            
            Your role:
            - Help diagnose crop diseases from descriptions
            - Provide practical farming advice
            - Answer questions about pest control, fertilizers, and irrigation
            - Suggest solutions in simple, actionable terms
            
            Communication style:
            - Be friendly and respectful
            - Use simple language farmers can understand
            - Keep responses brief (2-3 sentences)
            - Be practical and solution-focused
            - If you don't know something, admit it and suggest consulting a local agricultural officer
            
            Topics you help with:
            - Crop diseases (rice, vegetables, fruits)
            - Pest management
            - Soil health
            - Water management
            - Fertilizer recommendations
            - Planting schedules
            - Weather-related advice""",
        )

server = AgentServer()

def prewarm(proc: JobProcess):
    """Preload models for faster startup"""
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session(agent_name="agri-assistant")
async def agri_agent(ctx: JobContext):
    """Main agent entry point"""
    
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    logger.info(f"AGRI Agent joining room: {ctx.room.name}")
    
    # Set up voice AI pipeline
    # Using LiveKit Inference for STT/TTS (requires LiveKit Cloud or self-hosted inference)
    # For AWS-only solution, replace with AWS Transcribe/Polly
    session = AgentSession(
        # Speech-to-text
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        
        # LLM - Using AWS Bedrock Claude
        llm=inference.LLM(
            model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            # For Bedrock, you need to configure AWS credentials
        ),
        
        # Text-to-speech
        tts=inference.TTS(
            model="cartesia/sonic-3", 
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"  # Friendly female voice
        ),
        
        # Voice activity detection
        vad=ctx.proc.userdata["vad"],
    )
    
    # Start the session
    await session.start(
        agent=AGRIAssistant(),
        room=ctx.room,
    )
    
    # Connect to the room
    await ctx.connect()
    
    logger.info("AGRI Agent ready and listening!")

if __name__ == "__main__":
    cli.run_app(server)
