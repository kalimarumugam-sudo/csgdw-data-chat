# LLM Provider Switching Guide

This application supports both OpenAI and AWS Bedrock as LLM providers. You can easily switch between them by commenting/uncommenting lines in `ai_service.py`.

## Current Configuration

By default, the app uses **OpenAI GPT-4**.

## How to Switch Providers

### Option 1: Use OpenAI GPT-4 (Default)

In `ai_service.py`, ensure these lines are **uncommented**:
```python
# Lines 25-26
USE_OPENAI = True
client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
```

And these lines are **commented out**:
```python
# Lines 29-31
# USE_OPENAI = False
# from aws_config import aws_config, bedrock_config
# bedrock_client = aws_config.get_session().client('bedrock-runtime')
```

### Option 2: Use AWS Bedrock Claude 3.5 Sonnet

In `ai_service.py`, **comment out** these lines:
```python
# Lines 25-26
# USE_OPENAI = True
# client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
```

And **uncomment** these lines:
```python
# Lines 29-31
USE_OPENAI = False
from aws_config import aws_config, bedrock_config
bedrock_client = aws_config.get_session().client('bedrock-runtime')
```

## Required Environment Variables

### For OpenAI:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### For AWS Bedrock:
```bash
AWS_REGION=us-east-1
AWS_PROFILE=bedrock
BEDROCK_LLM_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

## Provider Differences

| Feature | OpenAI GPT-4 | AWS Bedrock Claude 3.5 |
|---------|--------------|-------------------------|
| **Streaming** | ✅ Real-time | ❌ Full response |
| **Cost** | Pay per token | Pay per token |
| **Setup** | API key only | AWS credentials + profile |
| **Models** | GPT-4, GPT-3.5 | Claude 3.5 Sonnet |
| **Response Quality** | Excellent | Excellent |

## Visual Indicator

The app will show the current provider in the sidebar:
- 🤖 **OpenAI GPT-4** - when using OpenAI
- 🧠 **AWS Bedrock Claude 3.5** - when using Bedrock

## Testing

After switching providers:
1. Restart the Streamlit app
2. Check the sidebar for the provider indicator
3. Test a simple query like "Show me the first 5 rows"
4. Verify the response and SQL generation works correctly

## Troubleshooting

### OpenAI Issues:
- Check `OPENAI_API_KEY` in `.env` file
- Verify API key is valid and has credits

### Bedrock Issues:
- Check AWS credentials in `~/.aws/credentials`
- Verify Bedrock model access in AWS console
- Test connection with `python3 test_bedrock.py`
