import enum
import sys

class OS(enum.Enum):
    '''
    An enumeration to represent the operating system type.
    '''

    POSIX = 'posix'
    WINDOWS = 'windows'
    
def get_os() -> OS:
    '''
    Get the current operating system as an _OS enum value. This function checks the 
    platform and returns the appropriate enum value for POSIX or Windows systems.
    '''

    if sys.platform == 'win32': return OS.WINDOWS
    else: return OS.POSIX