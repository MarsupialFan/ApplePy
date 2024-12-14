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

    def _run_simple_statement(self, statement) -> str:
        """Sends the given simple statement to the application."""
        script = AppleScript(f'tell application "{self.name}" to {statement}')
        return script.run()

    def _run_compound_statement(self, statement) -> str:
        """Sends the given compound statement to the application."""
        script = AppleScript(f'''
            tell application "{self.name}"
                {statement}
            end tell''')
        return script.run()

    def activate(self) -> None:
        """Bring the application to the foreground."""
        self._run_simple_statement('activate')

    def quit(self) -> None:
        """Quit the application."""
        self._run_simple_statement('quit')

    def is_running(self) -> bool:
        """Check if the application is currently running."""
        system_events = Application("System Events")
        is_running = system_events._run_simple_statement(f'exists (process "{self.name}")')
        return is_running.lower() == 'true'

    def get_number_of_windows(self) -> int:
        """Retrieve the number of this application's windows."""
        return int(self._run_simple_statement('get the number of windows'))

    def get_windows(self) -> List[str]:
        """Retrieve the list of all window names of the application."""
        windows_str = self._run_compound_statement('get the name of every window')
        return windows_str.split(', ') if windows_str else []
