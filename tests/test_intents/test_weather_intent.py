"""Tests for weather intent handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from agent.intents.weather import WeatherHandler
from agent.intents.base import IntentContext


class TestWeatherHandler:
    """Test cases for WeatherHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = WeatherHandler()
        self.mock_context = Mock(spec=IntentContext)
        self.mock_context.commands = Mock()
        self.mock_context.commands.maybe_run = AsyncMock()

    def test_matches_weather_queries(self):
        """Test that weather queries are matched correctly."""
        weather_queries = [
            "weather",
            "Weather",
            "WEATHER",
            "weather in London",
            "Weather in New York",
            "weather for Paris",
            "Weather for Tokyo"
        ]
        
        for query in weather_queries:
            assert self.handler.matches(query), f"Should match: {query}"

    def test_does_not_match_non_weather_queries(self):
        """Test that non-weather queries are not matched."""
        non_weather_queries = [
            "What's the time?",
            "What's the date?",
            "Hello world",
            "List files",
            "What's my IP?",
            "Whether or not"  # Contains 'weather' sound but not weather query
        ]
        
        for query in non_weather_queries:
            assert not self.handler.matches(query), f"Should not match: {query}"

    @pytest.mark.asyncio
    async def test_handle_windows_command_with_city(self):
        """Test handling with city on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.weather.OS.is_windows", lambda: True)
            
            await self.handler.handle("weather in London", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "curl.exe -s https://wttr.in/London"
            )

    @pytest.mark.asyncio
    async def test_handle_windows_command_without_city(self):
        """Test handling without city on Windows."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.weather.OS.is_windows", lambda: True)
            
            await self.handler.handle("weather", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "curl.exe -s https://wttr.in"
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command_with_city(self):
        """Test handling with city on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.weather.OS.is_windows", lambda: False)
            
            await self.handler.handle("weather in Paris", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "curl -s https://wttr.in/Paris"
            )

    @pytest.mark.asyncio
    async def test_handle_unix_command_without_city(self):
        """Test handling without city on Unix-like systems."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.weather.OS.is_windows", lambda: False)
            
            await self.handler.handle("weather", self.mock_context)
            
            self.mock_context.commands.maybe_run.assert_called_once_with(
                "curl -s https://wttr.in"
            )

    @pytest.mark.asyncio
    async def test_handle_city_name_processing(self):
        """Test that city names are processed correctly."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("agent.intents.weather.OS.is_windows", lambda: False)
            
            # Test city with spaces
            await self.handler.handle("weather in New York", self.mock_context)
            self.mock_context.commands.maybe_run.assert_called_with(
                "curl -s https://wttr.in/New_York"
            )
            
            # Test city with punctuation
            await self.handler.handle("weather in St. Petersburg", self.mock_context)
            self.mock_context.commands.maybe_run.assert_called_with(
                "curl -s https://wttr.in/St._Petersburg"
            )

    @pytest.mark.asyncio
    async def test_handle_returns_true(self):
        """Test that handle returns True."""
        result = await self.handler.handle("weather", self.mock_context)
        assert result is True
