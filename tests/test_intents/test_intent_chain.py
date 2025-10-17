"""Tests for intent chain integration."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.chain import IntentChain
from agent.intents.base import IntentContext


class TestIntentChain:
    """Test cases for IntentChain."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()

    def test_init_with_handlers(self):
        """Test initialization with handlers."""
        handler1 = Mock()
        handler2 = Mock()
        chain = IntentChain([handler1, handler2])
        
        assert len(chain._handlers) == 2
        assert chain._handlers[0] == handler1
        assert chain._handlers[1] == handler2

    def test_init_with_empty_handlers(self):
        """Test initialization with empty handlers."""
        chain = IntentChain([])
        assert len(chain._handlers) == 0

    @pytest.mark.asyncio
    async def test_try_handle_first_handler_matches(self):
        """Test that first matching handler is used."""
        handler1 = Mock()
        handler1.matches.return_value = True
        handler1.handle = AsyncMock(return_value=True)
        
        handler2 = Mock()
        handler2.matches.return_value = True
        handler2.handle = AsyncMock(return_value=True)
        
        chain = IntentChain([handler1, handler2])
        
        result = await chain.try_handle("test input", self.mock_context)
        
        assert result is True
        handler1.matches.assert_called_once_with("test input")
        handler1.handle.assert_called_once_with("test input", self.mock_context)
        # Second handler should not be called
        handler2.matches.assert_not_called()
        handler2.handle.assert_not_called()

    @pytest.mark.asyncio
    async def test_try_handle_second_handler_matches(self):
        """Test that second handler is used when first doesn't match."""
        handler1 = Mock()
        handler1.matches.return_value = False
        
        handler2 = Mock()
        handler2.matches.return_value = True
        handler2.handle = AsyncMock(return_value=True)
        
        chain = IntentChain([handler1, handler2])
        
        result = await chain.try_handle("test input", self.mock_context)
        
        assert result is True
        handler1.matches.assert_called_once_with("test input")
        handler2.matches.assert_called_once_with("test input")
        handler2.handle.assert_called_once_with("test input", self.mock_context)

    @pytest.mark.asyncio
    async def test_try_handle_no_handler_matches(self):
        """Test that False is returned when no handler matches."""
        handler1 = Mock()
        handler1.matches.return_value = False
        
        handler2 = Mock()
        handler2.matches.return_value = False
        
        chain = IntentChain([handler1, handler2])
        
        result = await chain.try_handle("test input", self.mock_context)
        
        assert result is False
        handler1.matches.assert_called_once_with("test input")
        handler2.matches.assert_called_once_with("test input")
        # No handle methods should be called
        handler1.handle.assert_not_called()
        handler2.handle.assert_not_called()

    @pytest.mark.asyncio
    async def test_try_handle_handler_returns_false(self):
        """Test that False is returned when handler returns False."""
        handler1 = Mock()
        handler1.matches.return_value = True
        handler1.handle = AsyncMock(return_value=False)
        
        chain = IntentChain([handler1])
        
        result = await chain.try_handle("test input", self.mock_context)
        
        assert result is False
        handler1.matches.assert_called_once_with("test input")
        handler1.handle.assert_called_once_with("test input", self.mock_context)

