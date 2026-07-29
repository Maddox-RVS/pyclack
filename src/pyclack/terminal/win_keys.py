from readchar import key as K

WINDOWS_LABELS: dict[str, str] = {
    K.BACKSPACE: 'BACKSPACE',

    K.UP: 'UP',
    K.DOWN: 'DOWN',
    K.LEFT: 'LEFT',
    K.RIGHT: 'RIGHT',

    K.INSERT: 'INSERT',
    K.SUPR: 'DELETE', # alias
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

    K.ESC_2: 'ESC',
    K.ENTER_2: 'ENTER',
    K.ENTER: 'ENTER', # alias of CR
}