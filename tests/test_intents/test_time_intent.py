"""Tests for time intent handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.time_only import TimeHandler
from agent.intents.base import IntentContext


class TestTimeHandler:
    """Test cases for TimeHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = TimeHandler()
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()
        self.mock_context.commands.maybe_run = AsyncMock()

    def test_matches_time_queries(self):
        """Test that time queries are matched correctly."""
        time_queries = [
            "What's the time?",
            "what's the time",
            "Current time",
            "current time",
            "Local time",
            "local time",
            "Time now",
            "time right now",
            "WHAT'S THE TIME?"
        ]
        
        for query in time_queries:
            assert self.handler.matches(query), f"Should match: {query}"

    def test_does_not_match_non_time_queries(self):
        """Test that non-time queries are not matched."""
        non_time_queries = [
            "What's the date?",
            "Hello world",
            "Weather in London",
            "List files",
            "What's my IP?",
            "Time to go home",  # Contains 'time' but not a time query
            "It's time for lunch"  # Contains 'time' but not a time query
        ]
        
        for query in non_time_queries:
            assert not self.handler.matches(query), f"Should not match: {query}"

    @pytest.mark.asyncio
    async def test_handle_windows_command(self):
        """Test handling on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.time_only.OS.is_windows", lambda: True)
            
            await self.handler.handle("What's the time?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                'powershell -Command "Get-Date -Format HH:mm:ss"'
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command(self):
        """Test handling on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.time_only.OS.is_windows", lambda: False)
            
            await self.handler.handle("What's the time?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "date '+%T'"
            )

    @pytest.mark.asyncio
    async def test_handle_returns_true(self):
        """Test that handle returns True."""
        result = await self.handler.handle("What's the time?", self.mock_context)
        assert result is True
