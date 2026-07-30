from readchar import readkey, readchar, key, config
from . import base_key
import enum
import sys

config.INTERRUPT_KEYS = [] # disable CTRL_C interrupt handling in readchar, allowing for manual handling

class _OS(enum.Enum):
    _POSIX = 'posix'
    _WINDOWS = 'windows'
    
def _get_os() -> _OS:
    if sys.platform == 'win32': return _OS._WINDOWS
    else: return _OS._POSIX

def _get_labels() -> dict[str, str]:
    if _get_os() == _OS._POSIX:
        from .posix_keys import POSIX_LABELS
        return base_key.BASE_LABELS | POSIX_LABELS
    else:
        from .win_keys import WINDOWS_LABELS
        return base_key.BASE_LABELS | WINDOWS_LABELS 

class KeyReader:
    '''
    A class for reading keys from the terminal. Acts as a wrapper around the readchar library, 
    providing a simple interface for reading keys and characters from the terminal.
    '''

    @staticmethod
    def readkey() -> str:
        '''
        Reads a key from the terminal and returns it as a string. This method blocks until a key is pressed.
        Returns:
            str: The key that was pressed.
            
        POSIX:
         - `BACKSPACE`
         - `UP`, `DOWN`, `LEFT`, `RIGHT`
         - `INSERT`, `DELETE`, `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
         - `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12`
         - `SHIFT_TAB`, `CTRL_ALT_DELETE`, `ALT_A`, `CTRL_ALT_A`
        WINDOWS:
         - `BACKSPACE`
         - `UP`, `DOWN`, `LEFT`, `RIGHT`
         - `INSERT`, `DELETE`, `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
         - `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12`
         - `ESC`, `ENTER`
        '''

        key: str = readkey()
        return _get_labels().get(key, key)