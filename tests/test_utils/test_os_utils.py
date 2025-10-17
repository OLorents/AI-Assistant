"""Tests for OS utilities."""

import pytest
from unittest.mock import patch
from agent.utils.os_utils import OS


class TestOS:
    """Test cases for OS utility class."""

    def test_is_windows_true(self):
        """Test is_windows returns True on Windows."""
        with patch('platform.system', return_value='Windows'):
            assert OS.is_windows() is True

    def test_is_windows_false(self):
        """Test is_windows returns False on non-Windows."""
        with patch('platform.system', return_value='Linux'):
            assert OS.is_windows() is False

    def test_is_macos_true(self):
        """Test is_macos returns True on macOS."""
        with patch('platform.system', return_value='Darwin'):
            assert OS.is_macos() is True

    def test_is_macos_false(self):
        """Test is_macos returns False on non-macOS."""
        with patch('platform.system', return_value='Linux'):
            assert OS.is_macos() is False

    def test_is_linux_true(self):
        """Test is_linux returns True on Linux."""
        with patch('platform.system', return_value='Linux'):
            assert OS.is_linux() is True

    def test_is_linux_false(self):
        """Test is_linux returns False on non-Linux."""
        with patch('platform.system', return_value='Windows'):
            assert OS.is_linux() is False

    def test_shell_and_args_windows(self):
        """Test shell_and_args on Windows."""
        with patch('platform.system', return_value='Windows'):
            result = OS.shell_and_args("echo hello")
            assert result == ["cmd", "/c", "echo hello"]

    def test_shell_and_args_unix(self):
        """Test shell_and_args on Unix-like systems."""
        with patch('platform.system', return_value='Linux'):
            result = OS.shell_and_args("echo hello")
            assert result == ["sh", "-c", "echo hello"]

    def test_shell_and_args_macos(self):
        """Test shell_and_args on macOS."""
        with patch('platform.system', return_value='Darwin'):
            result = OS.shell_and_args("echo hello")
            assert result == ["sh", "-c", "echo hello"]

    def test_shell_and_args_case_insensitive(self):
        """Test that OS detection is case insensitive."""
        with patch('platform.system', return_value='WINDOWS'):
            assert OS.is_windows() is True
        
        with patch('platform.system', return_value='linux'):
            assert OS.is_linux() is True
        
        with patch('platform.system', return_value='DARWIN'):
            assert OS.is_macos() is True

