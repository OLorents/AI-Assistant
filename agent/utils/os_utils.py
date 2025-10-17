"""Operating system utilities."""

import platform
import shlex


class OS:
    """Operating system detection utilities."""
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system().lower() == "windows"
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system().lower() == "darwin"
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system().lower() == "linux"
    
    @staticmethod
    def shell_and_args(command: str) -> list[str]:
        """Convert a command string to shell and arguments for subprocess."""
        if OS.is_windows():
            # On Windows, use cmd.exe for shell commands
            return ["cmd", "/c", command]
        else:
            # On Unix-like systems, use sh
            return ["sh", "-c", command]

