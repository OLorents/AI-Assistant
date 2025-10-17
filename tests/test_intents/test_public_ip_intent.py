"""Tests for public IP intent handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.public_ip import PublicIpHandler
from agent.intents.base import IntentContext


class TestPublicIpHandler:
    """Test cases for PublicIpHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = PublicIpHandler()
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()
        self.mock_context.commands.maybe_run = AsyncMock()

    def test_matches_ip_queries(self):
        """Test that IP queries are matched correctly."""
        ip_queries = [
            "What's my IP?",
            "what's my ip",
            "My public IP",
            "my public ip",
            "External IP",
            "external ip",
            "IP",
            "ip",
            "What is my IP?",
            "WHAT IS MY IP"
        ]
        
        for query in ip_queries:
            assert self.handler.matches(query), f"Should match: {query}"

    def test_does_not_match_non_ip_queries(self):
        """Test that non-IP queries are not matched."""
        non_ip_queries = [
            "What's the time?",
            "What's the date?",
            "Hello world",
            "Weather in London",
            "List files",
            "IP address configuration",  # Contains 'IP' but not a query
            "IP configuration"  # Contains 'IP' but not a query
        ]
        
        for query in non_ip_queries:
            assert not self.handler.matches(query), f"Should not match: {query}"

    @pytest.mark.asyncio
    async def test_handle_windows_command(self):
        """Test handling on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.public_ip.OS.is_windows", lambda: True)
            
            await self.handler.handle("What's my IP?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                'powershell -Command "(Invoke-RestMethod \'https://ifconfig.me/ip\')"'
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command(self):
        """Test handling on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.public_ip.OS.is_windows", lambda: False)
            
            await self.handler.handle("What's my IP?", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "curl -s https://ifconfig.me"
            )

    @pytest.mark.asyncio
    async def test_handle_returns_true(self):
        """Test that handle returns True."""
        result = await self.handler.handle("What's my IP?", self.mock_context)
        assert result is True
