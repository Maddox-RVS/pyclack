from . import os_utils
import sys

class EchoController:
    
      @staticmethod
      def is_ctl_echo_enabled() -> bool:
          if os_utils.get_os() == os_utils.OS.POSIX:
              import termios

              fd = sys.stdin.fileno()
              settings = termios.tcgetattr(fd)
              return bool(settings[3] & termios.ECHOCTL)
          return True


      @staticmethod
      def disable_ctl_echo() -> None:
          if os_utils.get_os() == os_utils.OS.POSIX:
              import termios

              fd = sys.stdin.fileno()
              settings = termios.tcgetattr(fd)
              settings[3] &= ~termios.ECHOCTL
              termios.tcsetattr(fd, termios.TCSANOW, settings)


      @staticmethod
      def enable_ctl_echo() -> None:
          if os_utils.get_os() == os_utils.OS.POSIX:
              import termios

              fd = sys.stdin.fileno()
              settings = termios.tcgetattr(fd)
              settings[3] |= termios.ECHOCTL
              termios.tcsetattr(fd, termios.TCSANOW, settings)