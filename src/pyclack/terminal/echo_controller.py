from . import os_utils
import sys

class EchoController:
    '''
    A utility class to manage the terminal's control character echo state.
    '''
    
    @staticmethod
    def is_ctl_echo_enabled() -> bool:
        '''
        Checks if the terminal's control character echo is enabled.

        This function only has an effect on POSIX-compliant systems. On other operating systems, it always returns True.

        Returns:
            bool: True if control character echo is enabled, False otherwise.
        '''

        if os_utils.get_os() == os_utils.OS.POSIX:
            import termios

            fd = sys.stdin.fileno()
            settings = termios.tcgetattr(fd)
            return bool(settings[3] & termios.ECHOCTL)
        return True


    @staticmethod
    def disable_ctl_echo() -> None:
        '''
        Disables the terminal's control character echo, preventing control characters from being displayed in the terminal.

        This function only has an effect on POSIX-compliant systems. On other operating systems, it does nothing.
        '''

        if os_utils.get_os() == os_utils.OS.POSIX:
            import termios

            fd = sys.stdin.fileno()
            settings = termios.tcgetattr(fd)
            settings[3] &= ~termios.ECHOCTL
            termios.tcsetattr(fd, termios.TCSANOW, settings)


    @staticmethod
    def enable_ctl_echo() -> None:
        '''
        Enables the terminal's control character echo, allowing control characters to be displayed in the terminal.

        This function only has an effect on POSIX-compliant systems. On other operating systems, it does nothing.
        '''

        if os_utils.get_os() == os_utils.OS.POSIX:
            import termios

            fd = sys.stdin.fileno()
            settings = termios.tcgetattr(fd)
            settings[3] |= termios.ECHOCTL
            termios.tcsetattr(fd, termios.TCSANOW, settings)