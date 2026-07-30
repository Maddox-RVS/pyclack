from .symbols import Symbols, Symbol, SpinnerSymbols
from typing import Optional

class Style:
    '''
    A class representing the style attributes for a theme, including background color, foreground color, 
    and text formatting options such as bold, underline, italic, and strikethrough.
    '''

    def __init__(self, 
        bg_color: Optional[str] = None,
        fg_color: Optional[str] = None,
        bold: bool = False,
        underline: bool = False,
        italic: bool = False,
        strikethrough: bool = False):
        '''
        Initialize a Style object with the given attributes.

        Args:
            bg_color (Optional[str]): Background color of the theme.
            fg_color (Optional[str]): Foreground color of the theme.
            bold (bool): Whether the text is bold.
            underline (bool): Whether the text is underlined.
            italic (bool): Whether the text is italicized.
            strikethrough (bool): Whether the text has a strikethrough.
        '''

        self.bg_color: Optional[str] = bg_color
        self.fg_color: Optional[str] = fg_color
        self.bold: bool = bold
        self.underline: bool = underline
        self.italic: bool = italic
        self.strikethrough: bool = strikethrough

class Theme:
    '''
    A class representing a theme, which consists of various styles for different elements and symbols used in the rendering process.
    '''

    def __init__(self, 
        active: Style,
        submit: Style,
        cancel: Style,
        error: Style,
        info: Style,
        muted: Style,
        text: Style,
        cursor: Style,
        symbols: Symbols):
        '''
        Initialize a Theme object with the given styles.

        Args:
            active (Style): Style for active elements.
            submit (Style): Style for submit elements.
            cancel (Style): Style for cancel elements.
            error (Style): Style for error elements.
            info (Style): Style for info elements.
            muted (Style): Style for muted elements.
            text (Style): Style for general text.
            cursor (Style): Style for the cursor.
            symbols (Symbols): Symbols to use in the theme.
        '''

        self.active: Style = active
        self.submit: Style = submit
        self.cancel: Style = cancel
        self.error: Style = error
        self.info: Style = info
        self.muted: Style = muted
        self.text: Style = text
        self.cursor: Style = cursor
        self.symbols: Symbols = symbols

class Themes:
    '''
    A class representing a collection of themes, including a default theme.
    '''

    DEFAULT: Theme = Theme(
        active   = Style(fg_color='cyan'),
        submit   = Style(fg_color='green'),
        cancel   = Style(fg_color='red'),
        error    = Style(fg_color='yellow'),
        info     = Style(fg_color='blue'),
        muted    = Style(fg_color='bright_black'),
        text     = Style(fg_color='white'),
        cursor   = Style(fg_color='black', bg_color='white'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('◆', '*'),
            step_marker_cancel                  = Symbol('■', 'x'),
            step_marker_error                   = Symbol('▲', 'x'),
            step_marker_submit                  = Symbol('◇', 'o'),
            connector_bar_start                 = Symbol('┌', 'T'),
            connector_bar_vertical              = Symbol('│', '|'),
            connector_bar_end                   = Symbol('└', '—'),
            selection_widget_radio_active       = Symbol('●', '>'),
            selection_widget_radio_inactive     = Symbol('○', ' '),
            selection_widget_checkbox_active    = Symbol('◻', '[•]'),
            selection_widget_checkbox_selected  = Symbol('◼', '[+]'),
            selection_widget_checkbox_inactive  = Symbol('◻', '[ ]'),
            selection_widget_password_mask      = Symbol('▪', '•'),
            box_drawing_horizontal_bar          = Symbol('─', '-'),
            box_drawing_top_right_corner        = Symbol('╮', '+'),
            box_drawing_left_connector          = Symbol('├', '+'),
            box_drawing_bottom_right_corner     = Symbol('╯', '+'),
            log_level_info                      = Symbol('●', '•'),
            log_level_success                   = Symbol('◆', '*'),
            log_level_warn                      = Symbol('▲', '!'),
            log_level_error                     = Symbol('■', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('◒', '◐', '◓', '◑'), 
                                                    ascii_symbols=('•', 'o', 'O', '0'))
        )
    )