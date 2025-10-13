"""Unit tests for CLI main entry point."""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from agent.cli.application import main_async


class TestMainEntryPoint:
    """Test cases for CLI main entry point."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        # Test that the main function can be imported and called
        from agent.cli.application import main
        assert callable(main)

    @pytest.mark.asyncio
    async def test_main_async_creates_application(self):
        """Test that main_async creates Application instance."""
        with patch('agent.cli.application.Application') as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run = AsyncMock()
            
            await main_async(["script", "test"])
            
            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once_with(["script", "test"])

    @pytest.mark.asyncio
    async def test_main_async_with_different_args(self):
        """Test main_async with different argument combinations."""
        with patch('agent.cli.application.Application') as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run = AsyncMock()
            
            # Test with no arguments
            await main_async([])
            mock_app.run.assert_called_with([])
            
            # Test with multiple arguments
            await main_async(["script", "--model=gpt-4", "Hello"])
            mock_app.run.assert_called_with(["script", "--model=gpt-4", "Hello"])


    def test_main_async_function_exists(self):
        """Test that main_async function exists and is callable."""
        from agent.cli.application import main_async
        assert callable(main_async)
