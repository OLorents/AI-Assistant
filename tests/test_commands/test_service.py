"""Tests for command service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agent.commands.service import CommandService


class TestCommandService:
    """Test cases for CommandService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_runner = Mock()
        self.mock_confirmation = Mock()
        self.service = CommandService(self.mock_runner, self.mock_confirmation)

    @pytest.mark.asyncio
    async def test_maybe_run_with_confirmation(self):
        """Test running a command when user confirms."""
        self.mock_confirmation.confirm = AsyncMock(return_value=True)
        self.mock_runner.run = AsyncMock(return_value=(0, "output", ""))
        
        with patch('builtins.print') as mock_print:
            await self.service.maybe_run("test command")
            
            self.mock_confirmation.confirm.assert_called_once_with("test command")
            self.mock_runner.run.assert_called_once_with("test command")
            
            # Check that output was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("> Running the command..." in call for call in print_calls)
            assert any("output" in call for call in print_calls)
            assert any("(exit 0)" in call for call in print_calls)

    @pytest.mark.asyncio
    async def test_maybe_run_without_confirmation(self):
        """Test skipping a command when user doesn't confirm."""
        self.mock_confirmation.confirm = AsyncMock(return_value=False)
        
        with patch('builtins.print') as mock_print:
            await self.service.maybe_run("test command")
            
            self.mock_confirmation.confirm.assert_called_once_with("test command")
            self.mock_runner.run.assert_not_called()
            
            # Check that skip message was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Skipping execution." in call for call in print_calls)

    @pytest.mark.asyncio
    async def test_maybe_run_with_stderr(self):
        """Test running a command that produces stderr."""
        self.mock_confirmation.confirm = AsyncMock(return_value=True)
        self.mock_runner.run = AsyncMock(return_value=(1, "output", "error message"))
        
        with patch('builtins.print') as mock_print:
            await self.service.maybe_run("test command")
            
            # Check that stderr was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("error message" in call for call in print_calls)
            assert any("(exit 1)" in call for call in print_calls)

    @pytest.mark.asyncio
    async def test_maybe_run_with_empty_output(self):
        """Test running a command with empty output."""
        self.mock_confirmation.confirm = AsyncMock(return_value=True)
        self.mock_runner.run = AsyncMock(return_value=(0, "", ""))
        
        with patch('builtins.print') as mock_print:
            await self.service.maybe_run("test command")
            
            # Check that only exit code was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("(exit 0)" in call for call in print_calls)
            # Should not print empty stdout or stderr
            # The "Command output" header will be printed even with empty output
            assert any("Command output" in call for call in print_calls)

    @pytest.mark.asyncio
    async def test_maybe_run_with_whitespace_output(self):
        """Test running a command with whitespace-only output."""
        self.mock_confirmation.confirm = AsyncMock(return_value=True)
        self.mock_runner.run = AsyncMock(return_value=(0, "   \n  ", "  \t  "))
        
        with patch('builtins.print') as mock_print:
            await self.service.maybe_run("test command")
            
            # Check that whitespace-only output is not printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("(exit 0)" in call for call in print_calls)
            # Should not print whitespace-only content
            assert not any("   " in call for call in print_calls)
