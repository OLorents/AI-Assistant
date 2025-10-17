"""Tests for date intent handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.date_only import DateHandler
from agent.intents.base import IntentContext


class TestDateHandler:
    """Test cases for DateHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = DateHandler()
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()
        self.mock_context.commands.maybe_run = AsyncMock()

    def test_matches_date_queries(self):
        """Test that date queries are matched correctly."""
        date_queries = [
            "What's the date?",
            "what's the date",
            "Current date",
            "current date",
            "Today's date",
            "today's date",
            "Date today",
            "date now",
            "WHAT'S THE DATE?"
        ]
        
        for query in date_queries:
            assert self.handler.matches(query), f"Should match: {query}"

    def test_does_not_match_non_date_queries(self):
        """Test that non-date queries are not matched."""
        non_date_queries = [
            "What's the time?",
            "Hello world",
            "Weather in London",
            "List files",
            "What's my IP?",
            "Date of birth",  # Contains 'date' but not a date query
            "Important date"  # Contains 'date' but not a date query
        ]
        
        for query in non_date_queries:
            assert not self.handler.matches(query), f"Should not match: {query}"

    @pytest.mark.asyncio
    async def test_handle_windows_command(self):
        """Test handling on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.date_only.OS.is_windows", lambda: True)
            
            await self.handler.handle("What's the date?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                'powershell -Command "Get-Date -Format yyyy-MM-dd"'
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command(self):
        """Test handling on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.date_only.OS.is_windows", lambda: False)
            
            await self.handler.handle("What's the date?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "date '+%Y-%m-%d'"
            )

    @pytest.mark.asyncio
    async def test_handle_returns_true(self):
        """Test that handle returns True."""
        result = await self.handler.handle("What's the date?", self.mock_context)
        assert result is True
