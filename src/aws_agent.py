import logging
import asyncio
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import silero
import boto3
import json

logger = logging.getLogger("agri-agent")
load_dotenv(".env.local")

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
polly = boto3.client('polly', region_name='ap-southeast-1')

async def entrypoint(ctx: JobContext):
    logger.info(f"AGRI Agent joining room: {ctx.room.name}")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for farmer to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Farmer connected: {participant.identity}")
    
    # Greet the farmer using Polly
    greeting = "Hello! Welcome to AGRI. I'm your AI agricultural assistant. How can I help you with your farming today?"
    await speak_text(ctx, greeting)
    
    # Set up VAD for voice detection
    vad = silero.VAD.load()
    
    # Listen for audio from farmer
    async def on_track_subscribed(track, publication, participant):
        if track.kind == "audio":
            logger.info(f"Subscribed to audio track from {participant.identity}")
            # TODO: Process audio with STT and respond with Claude
    
    ctx.room.on("track_subscribed", on_track_subscribed)
    
    logger.info("AGRI Agent ready and listening!")

async def speak_text(ctx: JobContext, text: str):
    """Convert text to speech using AWS Polly and play in room"""
    try:
        logger.info(f"Speaking: {text}")
        
        # Generate speech with Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='pcm',
            VoiceId='Joanna',
            Engine='neural',
            SampleRate='16000'
        )
        
        audio_data = response['AudioStream'].read()
        logger.info(f"Generated audio: {len(audio_data)} bytes")
        
        # TODO: Play audio in room using LiveKit audio track
        # For now, just log
        logger.info("Audio generated successfully")
        
    except Exception as e:
        logger.error(f"Error speaking: {e}")

async def ask_claude(prompt: str) -> str:
    """Ask Claude via AWS Bedrock"""
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "system": "You are AGRI, an AI agricultural assistant for Sri Lankan farmers. Help diagnose crop diseases, provide farming advice, and answer agricultural questions. Be friendly, concise, and practical. Speak in simple terms."
        })
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        logger.error(f"Error asking Claude: {e}")
        return "I'm sorry, I'm having trouble processing that right now."

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="AGRI Assistant"))
