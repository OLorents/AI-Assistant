"""Unit tests for CLI Application class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agent.cli.application import Application
from agent.cli.args import ArgParser
from agent.config.provider import EnvConfigProvider
from agent.core.assistant import AssistantService
from agent.core.history import HistoryManager


class TestApplication:
    """Test cases for Application class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cfg = Mock(spec=EnvConfigProvider)
        self.mock_arg_parser = Mock(spec=ArgParser)
        self.app = Application(self.mock_cfg, self.mock_arg_parser)

    def test_init(self):
        """Test Application initialization."""
        assert self.app._cfg == self.mock_cfg
        assert self.app._arg_parser == self.mock_arg_parser

    @patch('agent.cli.application.signal.signal')
    def test_configure_ctrl_c_success(self, mock_signal):
        """Test successful Ctrl+C configuration."""
        Application.configure_ctrl_c()
        mock_signal.assert_called_once()

    @patch('agent.cli.application.signal.signal')
    def test_configure_ctrl_c_exception(self, mock_signal):
        """Test Ctrl+C configuration with exception."""
        mock_signal.side_effect = Exception("Signal error")
        # Should not raise exception
        Application.configure_ctrl_c()

    @pytest.mark.asyncio
    async def test_process_query_success(self):
        """Test successful query processing."""
        mock_assistant = Mock(spec=AssistantService)
        mock_assistant.answer = AsyncMock(return_value="Test answer")
        
        with patch('builtins.print') as mock_print:
            await self.app.process_query("Test question", mock_assistant)
            
            mock_assistant.answer.assert_called_once_with("Test question")
            mock_print.assert_any_call("\nAnswer:")
            mock_print.assert_any_call("Test answer")
            mock_print.assert_any_call("\nCan I help you with anything else?")

    @pytest.mark.asyncio
    async def test_process_query_exception(self):
        """Test query processing with exception."""
        mock_assistant = Mock(spec=AssistantService)
        mock_assistant.answer = AsyncMock(side_effect=Exception("LLM error"))
        
        with patch('builtins.print') as mock_print:
            await self.app.process_query("Test question", mock_assistant)
            
            mock_print.assert_called_with("LLM error: LLM error")

    @pytest.mark.asyncio
    async def test_process_query_empty_answer(self):
        """Test query processing with empty answer."""
        mock_assistant = Mock(spec=AssistantService)
        mock_assistant.answer = AsyncMock(return_value="")
        
        with patch('builtins.print') as mock_print:
            await self.app.process_query("Test question", mock_assistant)
            
            mock_print.assert_called_with("No answer.")


    def test_handle_history_command_clear(self):
        """Test history command handling for clear."""
        self.mock_arg_parser.parse_history_command.return_value = ("clear", None)
        mock_assistant = Mock(spec=AssistantService)
        
        with patch.object(self.app, '_clear_current_conversation') as mock_clear:
            self.app.handle_history_command(["history", "clear"], mock_assistant)
            mock_clear.assert_called_once_with(mock_assistant)


    def test_handle_history_command_help(self):
        """Test history command handling for help."""
        self.mock_arg_parser.parse_history_command.return_value = ("help", None)
        
        with patch.object(self.app, '_show_history_help') as mock_help:
            self.app.handle_history_command(["history", "help"])
            mock_help.assert_called_once()




    def test_clear_current_conversation_with_assistant(self):
        """Test clearing current conversation with assistant."""
        mock_assistant = Mock(spec=AssistantService)
        
        with patch('builtins.print') as mock_print:
            self.app._clear_current_conversation(mock_assistant)
            mock_assistant.clear_history.assert_called_once()
            mock_print.assert_called_with("Current conversation history cleared.")

    def test_clear_current_conversation_without_assistant(self):
        """Test clearing current conversation without assistant."""
        with patch('builtins.print') as mock_print:
            self.app._clear_current_conversation(None)
            mock_print.assert_called_with("No active conversation to clear.")


    def test_show_history_help(self):
        """Test showing history help."""
        with patch('builtins.print') as mock_print:
            self.app._show_history_help()
            
            # Check that print was called multiple times
            assert mock_print.call_count >= 3
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("History Commands:" in call for call in print_calls)
            assert any("history clear" in call for call in print_calls)
            assert any("history help" in call for call in print_calls)
