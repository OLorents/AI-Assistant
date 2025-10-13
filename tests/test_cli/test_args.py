"""Unit tests for CLI argument parsing."""

import pytest
from agent.cli.args import ArgParser


class TestArgParser:
    """Test cases for ArgParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ArgParser()

    def test_parse_simple_question(self):
        """Test parsing a simple question without options."""
        question, agent, model = self.parser.parse(["What", "is", "Python?"])
        assert question == "What is Python?"
        assert agent is None
        assert model is None

    def test_parse_with_agent_override(self):
        """Test parsing with agent override."""
        question, agent, model = self.parser.parse(["--agent=gemini", "Hello"])
        assert question == "Hello"
        assert agent == "gemini"
        assert model is None

    def test_parse_with_agent_separate(self):
        """Test parsing with agent as separate argument."""
        question, agent, model = self.parser.parse(["--agent", "openai", "Test"])
        assert question == "Test"
        assert agent == "openai"
        assert model is None

    def test_parse_with_model_override(self):
        """Test parsing with model override."""
        question, agent, model = self.parser.parse(["--model=gpt-4", "Help me"])
        assert question == "Help me"
        assert agent is None
        assert model == "gpt-4"

    def test_parse_with_model_separate(self):
        """Test parsing with model as separate argument."""
        question, agent, model = self.parser.parse(["--model", "gemini-2.5-flash", "Code"])
        assert question == "Code"
        assert agent is None
        assert model == "gemini-2.5-flash"

    def test_parse_with_both_overrides(self):
        """Test parsing with both agent and model overrides."""
        question, agent, model = self.parser.parse([
            "--agent=openai", "--model=gpt-4", "Explain", "AI"
        ])
        assert question == "Explain AI"
        assert agent == "openai"
        assert model == "gpt-4"

    def test_parse_mixed_order(self):
        """Test parsing with mixed order of arguments."""
        question, agent, model = self.parser.parse([
            "Write", "--model=gpt-4", "code", "--agent=gemini", "for", "me"
        ])
        assert question == "Write code for me"
        assert agent == "gemini"
        assert model == "gpt-4"

    def test_parse_empty_args(self):
        """Test parsing empty arguments."""
        question, agent, model = self.parser.parse([])
        assert question == ""
        assert agent is None
        assert model is None

    def test_parse_only_options(self):
        """Test parsing only options without question."""
        question, agent, model = self.parser.parse(["--agent=test", "--model=test-model"])
        assert question == ""
        assert agent == "test"
        assert model == "test-model"

    def test_normalize_agent_openai_variants(self):
        """Test agent normalization for OpenAI variants."""
        assert ArgParser.normalize_agent("openaiagent") == "openaiagent"
        assert ArgParser.normalize_agent("openai") == "openaiagent"
        assert ArgParser.normalize_agent("OpenAI") == "openaiagent"
        assert ArgParser.normalize_agent("OPENAI") == "openaiagent"

    def test_normalize_agent_gemini_variants(self):
        """Test agent normalization for Gemini variants."""
        assert ArgParser.normalize_agent("geminiagent") == "geminiagent"
        assert ArgParser.normalize_agent("gemini") == "geminiagent"
        assert ArgParser.normalize_agent("google") == "geminiagent"
        assert ArgParser.normalize_agent("Gemini") == "geminiagent"

    def test_normalize_agent_other(self):
        """Test agent normalization for other agents."""
        assert ArgParser.normalize_agent("customagent") == "customagent"
        assert ArgParser.normalize_agent("test") == "test"

    def test_normalize_agent_none(self):
        """Test agent normalization with None input."""
        assert ArgParser.normalize_agent(None) is None

    def test_is_history_command_true(self):
        """Test history command detection for valid commands."""
        assert self.parser.is_history_command(["history"]) is True
        assert self.parser.is_history_command(["hist"]) is True
        assert self.parser.is_history_command(["h"]) is True
        assert self.parser.is_history_command(["History"]) is True
        assert self.parser.is_history_command(["HIST"]) is True

    def test_is_history_command_false(self):
        """Test history command detection for invalid commands."""
        assert self.parser.is_history_command(["help"]) is False
        assert self.parser.is_history_command(["exit"]) is False
        assert self.parser.is_history_command(["hello"]) is False
        assert self.parser.is_history_command([]) is False


    def test_parse_history_command_clear(self):
        """Test parsing history clear command."""
        command, target_id = self.parser.parse_history_command(["history", "clear"])
        assert command == "clear"
        assert target_id is None

    def test_parse_history_command_reset(self):
        """Test parsing history reset command."""
        command, target_id = self.parser.parse_history_command(["history", "reset"])
        assert command == "clear"
        assert target_id is None


    def test_parse_history_command_help(self):
        """Test parsing history help command."""
        command, target_id = self.parser.parse_history_command(["history", "help"])
        assert command == "help"
        assert target_id is None

    def test_parse_history_command_invalid(self):
        """Test parsing invalid history command."""
        command, target_id = self.parser.parse_history_command(["history", "invalid"])
        assert command == "help"
        assert target_id is None

    def test_parse_history_command_no_args(self):
        """Test parsing history command with no arguments."""
        command, target_id = self.parser.parse_history_command(["history"])
        assert command == "help"
        assert target_id is None

    def test_parse_history_command_insufficient_args(self):
        """Test parsing history command with insufficient arguments."""
        command, target_id = self.parser.parse_history_command(["history", "show"])
        assert command == "help"
        assert target_id is None
