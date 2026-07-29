from readchar import key as K
from readchar import config

INTERRUPT_KEYS = config.INTERRUPT_KEYS

POSIX_LABELS: dict[str, str] = {
    K.BACKSPACE: 'BACKSPACE',

    K.UP: 'UP',
    K.DOWN: 'DOWN',
    K.LEFT: 'LEFT',
    K.RIGHT: 'RIGHT',

    K.INSERT: 'INSERT',
    K.SUPR: 'DELETE', # SUPR is the raw name; DELETE is its alias
    K.HOME: 'HOME',
    K.END: 'END',
    K.PAGE_UP: 'PAGE_UP',
    K.PAGE_DOWN: 'PAGE_DOWN',

    K.F1: 'F1',
    K.F2: 'F2',
    K.F3: 'F3',
    K.F4: 'F4',
    K.F5: 'F5',
    K.F6: 'F6',
    K.F7: 'F7',
    K.F8: 'F8',
    K.F9: 'F9',
    K.F10: 'F10',
    K.F11: 'F11',
    K.F12: 'F12',

    K.SHIFT_TAB: 'SHIFT_TAB',
    K.CTRL_ALT_SUPR: 'CTRL_ALT_DELETE',
    K.ALT_A: 'ALT_A',
    K.CTRL_ALT_A: 'CTRL_ALT_A',

    K.ENTER: 'ENTER', # alias of LF
}