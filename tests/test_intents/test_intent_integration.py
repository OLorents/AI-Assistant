"""Integration tests for intent system."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agent.core.assistant import AssistantService
from agent.config.params import AiParameters
from agent.llm.interfaces import LLMClient
from agent.core.history import HistoryManager


class TestIntentIntegration:
    """Integration tests for intent system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=LLMClient)
        self.mock_client.complete = AsyncMock(return_value="LLM response")
        self.mock_client.complete_with_history = AsyncMock(return_value="LLM response")
        
        self.params = AiParameters(
            agent="test-agent",
            model="test-model",
            provider="stub",
            api_key="test-key",
            system_prompt="Test prompt"
        )
        
        self.history_manager = HistoryManager()

    @pytest.mark.asyncio
    async def test_assistant_with_intent_match(self):
        """Test that assistant uses intent when it matches."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        # Mock the command service to avoid stdin interaction
        mock_command_service = Mock()
        mock_command_service.maybe_run = AsyncMock()
        assistant._command_service = mock_command_service
        
        with patch('agent.core.assistant.IntentChain') as mock_chain_class:
            mock_chain = Mock()
            mock_chain.try_handle = AsyncMock(return_value=True)
            mock_chain_class.return_value = mock_chain
            
            result = await assistant.answer("What's the time?")
            
            # Should return intent handled message
            assert result == "Intent handled successfully."
            
            # Should not call LLM
            self.mock_client.complete.assert_not_called()
            self.mock_client.complete_with_history.assert_not_called()
            
            # Should add messages to history
            history = self.history_manager.get_conversation_history()
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "What's the time?"
            assert history[1]["role"] == "assistant"
            assert history[1]["content"] == "Intent handled successfully."

    @pytest.mark.asyncio
    async def test_assistant_without_intent_match(self):
        """Test that assistant uses LLM when no intent matches."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        with patch('agent.core.assistant.IntentChain') as mock_chain_class:
            mock_chain = Mock()
            mock_chain.try_handle = AsyncMock(return_value=False)
            mock_chain_class.return_value = mock_chain
            
            result = await assistant.answer("Hello, how are you?")
            
            # Should return LLM response
            assert result == "LLM response"
            
            # Should call LLM
            self.mock_client.complete.assert_called_once()
            
            # Should add messages to history
            history = self.history_manager.get_conversation_history()
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "Hello, how are you?"
            assert history[1]["role"] == "assistant"
            assert history[1]["content"] == "LLM response"

    @pytest.mark.asyncio
    async def test_assistant_creates_intent_chain(self):
        """Test that assistant creates intent chain with all handlers."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        # Check that intent chain was created
        assert assistant._intent_chain is not None
        assert len(assistant._intent_chain._handlers) == 6  # All intent handlers

    @pytest.mark.asyncio
    async def test_assistant_creates_command_service(self):
        """Test that assistant creates command service with proper components."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        # Check that command service was created
        assert assistant._command_service is not None
        
        # Check that it has runner and confirmation
        assert assistant._command_service._runner is not None
        assert assistant._command_service._confirmation is not None

    @pytest.mark.asyncio
    async def test_assistant_with_history_disabled(self):
        """Test that assistant works with history disabled."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        with patch('agent.core.assistant.IntentChain') as mock_chain_class:
            mock_chain = Mock()
            mock_chain.try_handle = AsyncMock(return_value=False)
            mock_chain_class.return_value = mock_chain
            
            result = await assistant.answer("Hello", use_history=False)
            
            # Should return LLM response
            assert result == "LLM response"
            
            # Should call LLM without history
            self.mock_client.complete.assert_called_once()
            self.mock_client.complete_with_history.assert_not_called()

    @pytest.mark.asyncio
    async def test_assistant_with_empty_input(self):
        """Test that assistant handles empty input."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        result = await assistant.answer("")
        
        assert result == "Please enter a non-empty request."
        
        # Should not call LLM or intents
        self.mock_client.complete.assert_not_called()
        self.mock_client.complete_with_history.assert_not_called()

    @pytest.mark.asyncio
    async def test_assistant_with_whitespace_input(self):
        """Test that assistant handles whitespace-only input."""
        assistant = AssistantService(self.params, self.mock_client, self.history_manager)
        
        result = await assistant.answer("   \n  \t  ")
        
        assert result == "Please enter a non-empty request."
        
        # Should not call LLM or intents
        self.mock_client.complete.assert_not_called()
        self.mock_client.complete_with_history.assert_not_called()
