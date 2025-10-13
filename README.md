# AI Assistant

A modern Python AI assistant with multi-provider support (OpenAI, Gemini) and a clean CLI interface.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env with your keys (example below)
copy .env.example .env   # Windows
# or
cp .env.example .env     # macOS/Linux

# Run the assistant
python -m agent.cli "What is machine learning?"
```

## Usage

```bash
# Interactive mode
python -m agent.cli

# One-shot questions
python -m agent.cli "Explain quantum computing"

# Override model
python -m agent.cli --agent=openaiagent "Why do we need AI"  
python -m agent.cli --agent=geminiagent "Why do we need AI"

## Configuration

Create a `.env` file:

# Optional agent name (used by your app)
AGENT=DefaultAgent
# or
AI_AGENT=DefaultAgent

# Google Gemini (preferred if present)
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

**Note**: If no API keys are provided, uses a stub client for testing.

## History Management
The AI Assistant maintains conversation history for context-aware interactions

## Features

- Multi-provider support (OpenAI, Gemini)
- Stub client for development without API keys
- Conversation history 
