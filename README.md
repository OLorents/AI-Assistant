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
python -m agent.cli --model=gpt-4 "Write Python code"

# History management
python -m agent.cli history list
python -m agent.cli history show <conversation_id>
python -m agent.cli history delete <conversation_id>
```

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

The AI Assistant maintains conversation history for context-aware interactions:

### Interactive Mode
- Conversations are automatically saved in memory during the session
- Each message builds context for subsequent responses
- Use `history help` in interactive mode for available commands

### History Commands
```bash
# List all saved conversations
python -m agent.cli history list

# View a specific conversation
python -m agent.cli history show <conversation_id>

# Delete a conversation
python -m agent.cli history delete <conversation_id>

# Clear current conversation (in interactive mode)
history clear

# Save current conversation (in interactive mode)
history save
```

### Storage
- Conversations are stored in `.history/` directory as JSON files
- Each conversation has a unique timestamp-based ID
- Messages include timestamps and role information

## Project Structure

```
agent/
├── cli/           # Command-line interface
├── config/        # Configuration management  
├── core/          # Core services
└── llm/           # LLM client implementations
```

## Features

- Multi-provider support (OpenAI, Gemini)
- Modern entry point (`python -m agent.cli`)
- Stub client for development without API keys
- Conversation history with persistent storage
- Interactive REPL with context awareness
- History management commands
