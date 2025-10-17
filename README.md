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

**Note**: If no API keys are provided, uses a stub client for testing.

## History Management
The AI Assistant maintains conversation history for context-aware interactions.

### History Commands

```bash
# Clear current conversation history
python -m agent.cli history clear

# Or in interactive mode:
history clear
```
## Features

- **Multi-provider support** (OpenAI, Gemini)
- **Stub client** for development without API keys
- **Conversation history** with context-aware interactions
- **History management** (clear history)
- **Intent system** with built-in handlers:
  - **Date & Time**: Get current date, time, or date-time
  - **File Operations**: List files and directories (ls/dir commands)
  - **Weather**: Get weather information for any city
  - **Network**: Check your public IP address
- **Command execution** with user confirmation for safety
- **Cross-platform support** (Windows, macOS, Linux)
- **Interactive CLI** with REPL mode
- **One-shot queries** for quick answers
- **Model override** support for different AI providers
- **Comprehensive test suite** (119 tests covering all functionality)
