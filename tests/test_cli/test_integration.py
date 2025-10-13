"""Integration tests for CLI workflow."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from agent.cli.application import Application, main_async
from agent.cli.args import ArgParser
from agent.config.provider import EnvConfigProvider
from agent.config.params import AiParameters
from agent.llm.factory import LLMClientFactory
from agent.core.assistant import AssistantService


class TestCLIIntegration:
    """Integration tests for CLI workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_cfg = Mock(spec=EnvConfigProvider)
        self.mock_arg_parser = Mock(spec=ArgParser)
        self.app = Application(self.mock_cfg, self.mock_arg_parser)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_one_shot_query_workflow(self):
        """Test complete one-shot query workflow."""
        # Mock the configuration
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            # Mock argument parsing
            self.mock_arg_parser.parse.return_value = ("Test question", None, None)
            self.mock_arg_parser.is_history_command.return_value = False
            
            # Mock LLM client factory
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                # Mock assistant service
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    mock_assistant.answer = AsyncMock(return_value="Test answer")
                    
                    with patch('builtins.print') as mock_print:
                        await self.app.run(["script", "Test question"])
                        
                        # Verify the workflow
                        mock_provider.load.assert_called_once()
                        self.mock_arg_parser.parse.assert_called_once_with(["Test question"])
                        mock_factory.create.assert_called_once_with(mock_params)
                        mock_assistant.answer.assert_called_once_with("Test question")
                        
                        # Verify output
                        mock_print.assert_any_call("Agent: test-agent | Provider: stub | Model: test-model")
                        mock_print.assert_any_call("\nAnswer:")
                        mock_print.assert_any_call("Test answer")

    @pytest.mark.asyncio
    async def test_one_shot_with_agent_override(self):
        """Test one-shot query with agent override."""
        mock_params = AiParameters(
            agent="default-agent",
            model="default-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            # Mock argument parsing with agent override
            self.mock_arg_parser.parse.return_value = ("Test question", "gemini", None)
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.ArgParser.normalize_agent', return_value="geminiagent"):
                with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                    mock_client = Mock()
                    mock_factory.create.return_value = mock_client
                    
                    with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                        mock_assistant = Mock()
                        mock_assistant_class.return_value = mock_assistant
                        mock_assistant.answer = AsyncMock(return_value="Test answer")
                        
                        with patch('builtins.print') as mock_print:
                            await self.app.run(["script", "--agent=gemini", "Test question"])
                            
                            # Verify agent override was applied
                            mock_print.assert_any_call("Agent: geminiagent | Provider: stub | Model: default-model")

    @pytest.mark.asyncio
    async def test_one_shot_with_model_override(self):
        """Test one-shot query with model override."""
        mock_params = AiParameters(
            agent="default-agent",
            model="default-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            # Mock argument parsing with model override
            self.mock_arg_parser.parse.return_value = ("Test question", None, "gpt-4")
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    mock_assistant.answer = AsyncMock(return_value="Test answer")
                    
                    with patch('builtins.print') as mock_print:
                        await self.app.run(["script", "--model=gpt-4", "Test question"])
                        
                        # Verify model override was applied
                        mock_print.assert_any_call("Agent: default-agent | Provider: stub | Model: gpt-4")

    @pytest.mark.asyncio
    async def test_history_command_workflow(self):
        """Test history command workflow."""
        # Mock argument parsing for history command
        self.mock_arg_parser.is_history_command.return_value = True
        self.mock_arg_parser.parse_history_command.return_value = ("clear", None)
        
        with patch.object(self.app, 'handle_history_command') as mock_handle:
            await self.app.run(["script", "history", "clear"])
            mock_handle.assert_called_once_with(["history", "clear"])

    @pytest.mark.asyncio
    async def test_repl_workflow_startup(self):
        """Test REPL workflow startup."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', side_effect=EOFError):
                            await self.app.run(["script"])
                            
                            # Verify startup messages
                            mock_print.assert_any_call("Agent: test-agent | Provider: stub | Model: test-model")
                            mock_print.assert_any_call("Type your request (or 'exit', 'history help' for history commands)")

    @pytest.mark.asyncio
    async def test_repl_exit_command(self):
        """Test REPL exit command."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', return_value="exit"):
                            await self.app.run(["script"])
                            
                            # Verify exit message
                            mock_print.assert_any_call("Bye!")

    @pytest.mark.asyncio
    async def test_repl_history_command(self):
        """Test REPL history command."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            # First call returns True for history command, second call raises EOFError to exit
            self.mock_arg_parser.is_history_command.side_effect = [True, False]
            self.mock_arg_parser.parse_history_command.return_value = ("help", None)
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', side_effect=["history help", EOFError]):
                            await self.app.run(["script"])
                            
                            # Verify history command was handled
                            mock_print.assert_any_call("Agent: test-agent | Provider: stub | Model: test-model")

    @pytest.mark.asyncio
    async def test_repl_query_processing(self):
        """Test REPL query processing."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            # First call returns False for history command, second call raises EOFError to exit
            self.mock_arg_parser.is_history_command.side_effect = [False, False]
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    mock_assistant.answer = AsyncMock(return_value="Test answer")
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', side_effect=["Test question", EOFError]):
                            await self.app.run(["script"])
                            
                            # Verify query was processed
                            mock_assistant.answer.assert_called_once_with("Test question")
                            mock_print.assert_any_call("\nAnswer:")
                            mock_print.assert_any_call("Test answer")

    @pytest.mark.asyncio
    async def test_error_handling_in_repl(self):
        """Test error handling in REPL."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    mock_assistant.answer = AsyncMock(side_effect=Exception("Test error"))
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', side_effect=["Test question", EOFError]):
                            await self.app.run(["script"])
                            
                            # Verify error was handled
                            mock_print.assert_any_call("LLM error: Test error")

    @pytest.mark.asyncio
    async def test_keyboard_interrupt_handling(self):
        """Test keyboard interrupt handling in REPL."""
        mock_params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test system prompt"
        )
        
        with patch('agent.cli.application.EnvConfigProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_provider.load.return_value = mock_params
            
            self.mock_arg_parser.is_history_command.return_value = False
            
            with patch('agent.cli.application.LLMClientFactory') as mock_factory:
                mock_client = Mock()
                mock_factory.create.return_value = mock_client
                
                with patch('agent.cli.application.AssistantService') as mock_assistant_class:
                    mock_assistant = Mock()
                    mock_assistant_class.return_value = mock_assistant
                    mock_assistant.answer = AsyncMock(side_effect=KeyboardInterrupt())
                    
                    with patch('builtins.print') as mock_print:
                        with patch('builtins.input', side_effect=["Test question", EOFError]):
                            await self.app.run(["script"])
                            
                            # Verify keyboard interrupt was handled
                            mock_print.assert_any_call("\nCanceled.")

    @pytest.mark.asyncio
    async def test_main_async_function(self):
        """Test main_async function."""
        with patch('agent.cli.application.Application') as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run = AsyncMock()
            
            await main_async(["script", "test"])
            
            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once_with(["script", "test"])
