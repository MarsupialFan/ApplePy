import platform
import subprocess

from typing import List

class ApplePyException(Exception):
    pass

class ScriptError(ApplePyException):
    pass

class UnsupportedError(ApplePyException):
    pass


class AppleScript:
    """Utility class for low-level AppleScript interactions."""

    def __init__(self, script: str) -> None:
        self.script = script

    def run(self) -> str:
        """Run the script and return its output.

        Returns:
            str: The output of the AppleScript command.
        
        Raises:
            RuntimeError: If the script execution fails.
        """
        if platform.system() != 'Darwin':
            raise UnsupportedError("AppleScript is only supported on macOS")

        try:
            result = subprocess.run(['osascript', '-e', self.script], capture_output=True, text=True, check=True)
            result.check_returncode()
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ScriptError(f"script error: {e.stderr}") from e


class Application:
    def __init__(self, name: str) -> None:
        self.name = name
    
    def activate(self) -> None:
        """Bring the application to the foreground."""

        script = AppleScript(f'tell application "{self.name}" to activate')
        script.run()
    
    def quit(self) -> None:
        """Quit the application."""

        script = AppleScript(f'tell application "{self.name}" to quit')
        script.run()
    
    def is_running(self) -> bool:
        """Check if the application is currently running."""

        script = AppleScript(f'''
            tell application "System Events"
                set isRunning to exists (process "{self.name}")
            end tell
            return isRunning
            ''')
        return script.run().lower() == 'true'

        
    def get_windows(self) -> List[str]:
        """Retrieve the list of all window names of the application."""
    
        script = AppleScript(f'''
            tell application "{self.name}"
                get the name of every window
            end tell
            ''')

        windows_str = script.run()
        return windows_str.split(', ') if windows_str else []