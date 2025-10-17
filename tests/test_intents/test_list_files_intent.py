"""Tests for list files intent handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.list_files import ListFilesHandler
from agent.intents.base import IntentContext


class TestListFilesHandler:
    """Test cases for ListFilesHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ListFilesHandler()
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()
        self.mock_context.commands.maybe_run = AsyncMock()

    def test_matches_list_files_queries(self):
        """Test that list files queries are matched correctly."""
        list_queries = [
            "list files",
            "List files",
            "show files",
            "Show files",
            "display files",
            "Display files",
            "print files",
            "Print files",
            "ls",
            "dir",
            "current files",
            "Current files"
        ]
        
        for query in list_queries:
            assert self.handler.matches(query), f"Should match: {query}"

    def test_does_not_match_non_list_queries(self):
        """Test that non-list queries are not matched."""
        non_list_queries = [
            "What's the time?",
            "What's the date?",
            "Hello world",
            "Weather in London",
            "What's my IP?",
            "file system",  # Contains 'file' but not a list query
            "My files are important"  # Contains 'files' but not a list query
        ]
        
        for query in non_list_queries:
            assert not self.handler.matches(query), f"Should not match: {query}"

    @pytest.mark.asyncio
    async def test_handle_windows_command_basic(self):
        """Test basic handling on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.list_files.OS.is_windows", lambda: True)
            
            await self.handler.handle("list files", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                'powershell -Command "Get-ChildItem "'
            )

    @pytest.mark.asyncio
    async def test_handle_windows_command_with_hidden(self):
        """Test handling with hidden files on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.list_files.OS.is_windows", lambda: True)
            
            await self.handler.handle("list all files", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                'powershell -Command "Get-ChildItem -Force"'
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command_basic(self):
        """Test basic handling on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.list_files.OS.is_windows", lambda: False)
            
            await self.handler.handle("list files", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "ls -l"
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command_with_hidden(self):
        """Test handling with hidden files on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.list_files.OS.is_windows", lambda: False)
            
            await self.handler.handle("list all files", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "ls -la"
            )

    @pytest.mark.asyncio
    async def test_handle_returns_true(self):
        """Test that handle returns True."""
        result = await self.handler.handle("list files", self.mock_context)
        assert result is True

