"""Tests for user confirmation components."""

import pytest
from unittest.mock import patch, Mock
from agent.commands.confirm import StdInConfirmation


class TestStdInConfirmation:
    """Test cases for StdInConfirmation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.confirmation = StdInConfirmation()

    @pytest.mark.asyncio
    async def test_confirm_with_y_response(self):
        """Test confirmation with 'y' response."""
        with patch('builtins.input', return_value="y"):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is True
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_yes_response(self):
        """Test confirmation with 'yes' response."""
        with patch('builtins.input', return_value="yes"):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is False  # Only 'y' is accepted
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_n_response(self):
        """Test confirmation with 'n' response."""
        with patch('builtins.input', return_value="n"):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is False
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_empty_response(self):
        """Test confirmation with empty response."""
        with patch('builtins.input', return_value=""):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is False
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_whitespace_response(self):
        """Test confirmation with whitespace response."""
        with patch('builtins.input', return_value="  y  "):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is True  # Should strip whitespace
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_uppercase_y(self):
        """Test confirmation with uppercase 'Y' response."""
        with patch('builtins.input', return_value="Y"):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is True  # Should be case insensitive
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_eof_error(self):
        """Test confirmation with EOFError."""
        with patch('builtins.input', side_effect=EOFError):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is False
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_with_keyboard_interrupt(self):
        """Test confirmation with KeyboardInterrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('builtins.print') as mock_print:
                result = await self.confirmation.confirm("test command")
                
                assert result is False
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_confirm_displays_command(self):
        """Test that confirmation displays the command."""
        with patch('builtins.input', return_value="n"):
            with patch('builtins.print') as mock_print:
                await self.confirmation.confirm("echo hello world")
                
                # Check that the command was displayed
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                assert any("echo hello world" in call for call in print_calls)

