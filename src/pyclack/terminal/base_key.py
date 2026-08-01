from readchar import key as K

BASE_LABELS: dict[str, str] = {
    K.SPACE: 'SPACE',
    K.ESC: 'ESC',

    K.LF: 'ENTER',
    K.CR: 'ENTER',
    K.TAB: 'TAB',

    K.CTRL_A: 'CTRL_A',
    K.CTRL_B: 'CTRL_B',
    K.CTRL_C: 'CTRL_C',
    K.CTRL_D: 'CTRL_D',
    K.CTRL_E: 'CTRL_E',
    K.CTRL_F: 'CTRL_F',
    K.CTRL_G: 'CTRL_G',
    K.CTRL_H: 'CTRL_H',
    # K.CTRL_I is the same as K.TAB (Tab)
    # K.CTRL_J is the same as K.LF (Enter)
    K.CTRL_K: 'CTRL_K',
    K.CTRL_L: 'CTRL_L',
    # K.CTRL_M is the same as K.CR (Enter)
    K.CTRL_N: 'CTRL_N',
    K.CTRL_O: 'CTRL_O',
    K.CTRL_P: 'CTRL_P',
    K.CTRL_Q: 'CTRL_Q',
    K.CTRL_R: 'CTRL_R',
    K.CTRL_S: 'CTRL_S',
    K.CTRL_T: 'CTRL_T',
    K.CTRL_U: 'CTRL_U',
    K.CTRL_V: 'CTRL_V',
    K.CTRL_W: 'CTRL_W',
    K.CTRL_X: 'CTRL_X',
    K.CTRL_Y: 'CTRL_Y',
    K.CTRL_Z: 'CTRL_Z',
}