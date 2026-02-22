# AGRI Voice Assistant Agent

## Project Overview

AGRI is an AI-powered agricultural assistant for Sri Lankan farmers, built with LiveKit Agents. The agent provides voice-based consultation for crop disease diagnosis, farming advice, and agricultural guidance.

## Architecture

- **Framework**: LiveKit Agents 1.4
- **LLM**: AWS Bedrock Claude 3.5 Sonnet
- **STT**: Deepgram Nova 3 (multilingual)
- **TTS**: Cartesia Sonic 3
- **VAD**: Silero VAD
- **Deployment**: AWS (Fargate/ECS)

## Key Features

1. **Voice-First Interface**: Farmers can speak naturally in Sinhala, Tamil, or English
2. **Agricultural Expertise**: Specialized in Sri Lankan crop diseases and farming practices
3. **Real-time Responses**: Low-latency voice interaction
4. **Offline Capability**: Flutter app has offline TFLite model fallback
5. **PDPA Compliance**: Privacy-first design with data anonymization

## File Structure

```
agri-agent/
├── src/
│   ├── agri_agent.py       # Main agent code
│   └── agent.py            # Original template (for reference)
├── .env.local              # Configuration
├── pyproject.toml          # Dependencies
└── README.md
```

## Configuration

### Environment Variables (.env.local)

```env
LIVEKIT_URL=wss://voice.thishanth.com
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<from-aws>
AWS_SECRET_ACCESS_KEY=<from-aws>
```

### AWS Services Used

- **Bedrock**: Claude 3.5 Sonnet for LLM
- **Polly**: Text-to-speech (fallback)
- **Transcribe**: Speech-to-text (fallback)
- **DynamoDB**: Farmer data and diagnostics
- **S3**: Image storage
- **SNS**: Alerts for agricultural officers

## Development

### Setup

```bash
# Install dependencies
uv sync

# Download models
uv run python src/agri_agent.py download-files

# Run in console mode
uv run python src/agri_agent.py console

# Run in dev mode
uv run python src/agri_agent.py dev
```

### Testing

```bash
# Run tests
uv run pytest

# Test with web interface
# Open voice_chat.html in browser
```

## Agent Behavior

### Conversation Flow

1. **Greeting**: "Hello! Welcome to AGRI. I'm your AI agricultural assistant. How can I help you with your farming today?"

2. **Listening**: Agent uses VAD to detect when farmer is speaking

3. **Processing**: 
   - STT converts speech to text
   - LLM (Claude) generates response
   - TTS converts response to speech

4. **Response**: Agent speaks back to farmer

### Example Interactions

**Farmer**: "My rice plants have brown spots on the leaves"
**AGRI**: "Brown spots on rice leaves could be brown spot disease caused by fungus. Try applying a copper-based fungicide and ensure proper drainage. If it spreads, contact your local agricultural officer."

**Farmer**: "When should I plant tomatoes?"
**AGRI**: "In Sri Lanka, the best time to plant tomatoes is during Yala season (April-May) or Maha season (October-November). Make sure soil is well-drained and rich in organic matter."

## Customization

### Adding New Features

1. **Custom Tools**: Add function tools to the AGRIAssistant class
2. **Knowledge Base**: Integrate with Bedrock Knowledge Base for RAG
3. **Image Analysis**: Add vision capabilities for crop disease diagnosis
4. **Multi-language**: Configure STT/TTS for Sinhala and Tamil

### Example: Adding Weather Tool

```python
from livekit.agents import function_tool, RunContext

@function_tool
async def get_weather(self, context: RunContext, location: str):
    """Get current weather for farming location
    
    Args:
        location: District or city name in Sri Lanka
    """
    # Call weather API
    return f"Weather in {location}: Sunny, 28°C"
```

## Production Deployment

### Docker Build

```bash
docker build -t agri-agent .
docker run -p 8080:8080 agri-agent
```

### AWS Fargate

```bash
# Deploy using CDK
cd ../
cdk deploy AgriAgentStack
```

## Monitoring

- **Logs**: CloudWatch Logs
- **Metrics**: LiveKit Analytics
- **Alerts**: SNS for errors

## Troubleshooting

### Agent Not Speaking

- Check API keys are set correctly
- Verify LiveKit server is running
- Check agent logs for errors

### Poor Audio Quality

- Ensure good microphone
- Check network latency
- Verify TTS voice settings

### LLM Errors

- Check AWS Bedrock access
- Verify model ID is correct
- Check rate limits

## Contributing

When modifying the agent:

1. Update instructions in AGRIAssistant class
2. Test with `uv run pytest`
3. Update this AGENTS.md file
4. Document any new environment variables

## Resources

- [LiveKit Agents Docs](https://docs.livekit.io/agents/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [AGRI Project README](../../README.md)
