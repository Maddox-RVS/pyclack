from readchar import readkey, config
from . import base_key
import enum
import sys

config.INTERRUPT_KEYS = [] # disable CTRL_C interrupt handling in readchar, allowing for manual handling

class _OS(enum.Enum):
    '''
    An enumeration to represent the operating system type.
    '''

    _POSIX = 'posix'
    _WINDOWS = 'windows'
    
def _get_os() -> _OS:
    '''
    Get the current operating system as an _OS enum value. This function checks the 
    platform and returns the appropriate enum value for POSIX or Windows systems.
    '''

    if sys.platform == 'win32': return _OS._WINDOWS
    else: return _OS._POSIX

def _get_labels() -> dict[str, str]:
    '''
    Get the appropriate key labels based on the operating system. This function returns a dictionary of key labels that are 
    specific to either POSIX or Windows systems, overriding any conflicting or duplicate base key labels.

    Returns:
        dict[str, str]: A dictionary mapping key codes to their corresponding labels for the current operating system.
    '''

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
        This function will catch a `KeyboardInterrupt` exception and return the string 'CTRL_C' instead of raising the exception.
        Returns:
            str: The key that was pressed.

        Note: **POSIX** and **WINDOWS** will override any conflicting/duplicate **BASE KEY** labels with their own specific labels. The following keys are supported:

        **BASE KEYS**:
         - `SPACE`, `ESC`, `ENTER`, `TAB`
         - `CTRL_A`, `CTRL_B`, `CTRL_C`, `CTRL_D`, `CTRL_E`, `CTRL_F`, `CTRL_G`, `CTRL_H`, 
        `CTRL_K`, `CTRL_L`, `CTRL_N`, `CTRL_O`, `CTRL_P`, `CTRL_Q`, `CTRL_R`, `CTRL_S`, 
        `CTRL_T`, `CTRL_U`, `CTRL_V`, `CTRL_W`, `CTRL_X`, `CTRL_Y`, `CTRL_Z`
            
        **POSIX**:
         - `BACKSPACE`
         - `UP`, `DOWN`, `LEFT`, `RIGHT`
         - `INSERT`, `DELETE`, `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
         - `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12`
         - `SHIFT_TAB`, `CTRL_ALT_DELETE`, `ALT_A`, `CTRL_ALT_A`
        **WINDOWS**:
         - `BACKSPACE`
         - `UP`, `DOWN`, `LEFT`, `RIGHT`
         - `INSERT`, `DELETE`, `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
         - `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12`
         - `ESC`, `ENTER`
        '''

        key: str = readkey()
        return _get_labels().get(key, key)