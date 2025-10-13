"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.config.params import AiParameters


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_ai_params():
    """Create mock AI parameters for testing."""
    return AiParameters(
        agent="test-agent",
        model="test-model",
        provider="stub",
        api_key="test-key",
        system_prompt="Test system prompt"
    )


@pytest.fixture
def mock_config_provider():
    """Create mock configuration provider."""
    provider = Mock()
    provider.load.return_value = AiParameters(
        agent="test-agent",
        model="test-model",
        provider="stub",
        api_key="test-key",
        system_prompt="Test system prompt"
    )
    return provider


@pytest.fixture
def mock_arg_parser():
    """Create mock argument parser."""
    parser = Mock()
    parser.parse.return_value = ("test question", None, None)
    parser.is_history_command.return_value = False
    parser.parse_history_command.return_value = ("list", None)
    return parser


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client."""
    client = Mock()
    client.complete = Mock()
    client.complete_with_history = Mock()
    return client


@pytest.fixture
def mock_assistant_service():
    """Create mock assistant service."""
    assistant = Mock()
    assistant.answer = Mock()
    assistant.clear_history = Mock()
    assistant.get_history_manager = Mock()
    return assistant


@pytest.fixture
def mock_history_manager():
    """Create mock history manager."""
    manager = Mock()
    manager.add_message = Mock()
    manager.get_conversation_history = Mock(return_value=[])
    manager.clear_current_conversation = Mock()
    return manager
