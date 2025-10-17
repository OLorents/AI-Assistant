"""Tests for command runner components."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agent.commands.runner import SubprocessRunner


class TestSubprocessRunner:
    """Test cases for SubprocessRunner."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = SubprocessRunner()

    @pytest.mark.asyncio
    async def test_run_powershell_command(self):
        """Test running a PowerShell command."""
        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = Mock()
            mock_proc.communicate = AsyncMock(return_value=(b"10:30:00", b""))
            mock_proc.returncode = 0
            mock_create.return_value = mock_proc
            
            code, stdout, stderr = await self.runner.run('powershell -Command "Get-Date -Format HH:mm:ss"')
            
            assert code == 0
            assert stdout == "10:30:00"
            assert stderr == ""
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[0] == ("powershell", "-Command", "Get-Date -Format HH:mm:ss")

    @pytest.mark.asyncio
    async def test_run_regular_command(self):
        """Test running a regular command."""
        with patch('agent.commands.runner.OS.shell_and_args', return_value=["cmd", "/c", "echo hello"]):
            with patch('asyncio.create_subprocess_exec') as mock_create:
                mock_proc = Mock()
                mock_proc.communicate = AsyncMock(return_value=(b"hello", b""))
                mock_proc.returncode = 0
                mock_create.return_value = mock_proc
                
                code, stdout, stderr = await self.runner.run("echo hello")
                
                assert code == 0
                assert stdout == "hello"
                assert stderr == ""
                mock_create.assert_called_once()
                call_args = mock_create.call_args
                assert call_args[0] == ("cmd", "/c", "echo hello")

    @pytest.mark.asyncio
    async def test_run_command_with_error(self):
        """Test running a command that returns an error."""
        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = Mock()
            mock_proc.communicate = AsyncMock(return_value=(b"", b"Command not found"))
            mock_proc.returncode = 1
            mock_create.return_value = mock_proc
            
            code, stdout, stderr = await self.runner.run("invalid-command")
            
            assert code == 1
            assert stdout == ""
            assert stderr == "Command not found"

    @pytest.mark.asyncio
    async def test_run_command_with_empty_output(self):
        """Test running a command with empty output."""
        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = Mock()
            mock_proc.communicate = AsyncMock(return_value=(None, None))
            mock_proc.returncode = 0
            mock_create.return_value = mock_proc
            
            code, stdout, stderr = await self.runner.run("empty-command")
            
            assert code == 0
            assert stdout == ""
            assert stderr == ""

    @pytest.mark.asyncio
    async def test_run_powershell_command_strips_quotes(self):
        """Test that PowerShell commands have quotes stripped properly."""
        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = Mock()
            mock_proc.communicate = AsyncMock(return_value=(b"output", b""))
            mock_proc.returncode = 0
            mock_create.return_value = mock_proc
            
            await self.runner.run('powershell -Command "Get-Date"')
            
            # Should strip the outer quotes from the PowerShell command
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[0] == ("powershell", "-Command", "Get-Date")
