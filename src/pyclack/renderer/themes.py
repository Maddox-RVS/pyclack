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
        strikethrough: bool = False,
        dim: bool = False):
        '''
        Initialize a Style object with the given attributes.
        All color attributes can either be a string representing a color name, a hexadecimal color code, or None for default terminal colors.

        Args:
            bg_color (str, optional): Background color of the theme.
            fg_color (str, optional): Foreground color of the theme.
            bold (bool, optional): Whether the text is bold.
            underline (bool, optional): Whether the text is underlined.
            italic (bool, optional): Whether the text is italicized.
            strikethrough (bool, optional): Whether the text has a strikethrough.
            dim (bool, optional): Whether to dim the text color
        '''

        self.bg_color: Optional[str] = bg_color
        self.fg_color: Optional[str] = fg_color
        self.bold: bool = bold
        self.underline: bool = underline
        self.italic: bool = italic
        self.strikethrough: bool = strikethrough
        self.dim = dim

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
        cursor   = Style(fg_color='bright_black', bg_color='white'),
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

    DARK: Theme = Theme(
        active   = Style(fg_color='#888888'),
        submit   = Style(fg_color='#4E6E58'),
        cancel   = Style(fg_color='#6E4E4E'),
        error    = Style(fg_color='#6E634E'),
        info     = Style(fg_color='#4E5C6E'),
        muted    = Style(fg_color='#3A3A3A'),
        text     = Style(fg_color='#A0A0A0'),
        cursor   = Style(fg_color='#121212', bg_color='#888888'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('▶', '>'),
            step_marker_cancel                  = Symbol('■', 'x'),
            step_marker_error                   = Symbol('▲', '!'),
            step_marker_submit                  = Symbol('▲', 'v'),
            connector_bar_start                 = Symbol('┌', '+'),
            connector_bar_vertical              = Symbol('│', '|'),
            connector_bar_end                   = Symbol('└', '\\'),
            selection_widget_radio_active       = Symbol('●', '(*)'),
            selection_widget_radio_inactive     = Symbol('○', '( )'),
            selection_widget_checkbox_active    = Symbol('■', '[x]'),
            selection_widget_checkbox_selected  = Symbol('■', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('□', '[ ]'),
            selection_widget_password_mask      = Symbol('*', '*'),
            box_drawing_horizontal_bar          = Symbol('─', '-'),
            box_drawing_top_right_corner        = Symbol('┐', '+'),
            box_drawing_left_connector          = Symbol('├', '+'),
            box_drawing_bottom_right_corner     = Symbol('┘', '+'),
            log_level_info                      = Symbol('●', 'i'),
            log_level_success                   = Symbol('◆', 'v'),
            log_level_warn                      = Symbol('▲', '!'),
            log_level_error                     = Symbol('■', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'), 
                                                    ascii_symbols=('|', '/', '-', '\\'))
        )
    )

    LIGHT: Theme = Theme(
        active   = Style(fg_color='#CBD5E1'),
        submit   = Style(fg_color='#DCFCE7'),
        cancel   = Style(fg_color='#FEE2E2'),
        error    = Style(fg_color='#FEF3C7'),
        info     = Style(fg_color='#E0F2FE'),
        muted    = Style(fg_color='#94A3B8'),
        text     = Style(fg_color='#FFFFFF'),
        cursor   = Style(fg_color='#000000', bg_color='#FFFFFF'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('✧', '*'),
            step_marker_cancel                  = Symbol('◌', 'o'),
            step_marker_error                   = Symbol('△', '!'),
            step_marker_submit                  = Symbol('✦', '+'),
            connector_bar_start                 = Symbol('┌', '+'),
            connector_bar_vertical              = Symbol('┊', '|'),
            connector_bar_end                   = Symbol('└', '\\'),
            selection_widget_radio_active       = Symbol('⦿', '(*)'),
            selection_widget_radio_inactive     = Symbol('◌', '( )'),
            selection_widget_checkbox_active    = Symbol('▣', '[x]'),
            selection_widget_checkbox_selected  = Symbol('⬔', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('⬚', '[ ]'),
            selection_widget_password_mask      = Symbol('⋄', '*'),
            box_drawing_horizontal_bar          = Symbol('┈', '-'),
            box_drawing_top_right_corner        = Symbol('┐', '+'),
            box_drawing_left_connector          = Symbol('├', '+'),
            box_drawing_bottom_right_corner     = Symbol('┘', '+'),
            log_level_info                      = Symbol('✧', 'i'),
            log_level_success                   = Symbol('✦', 'v'),
            log_level_warn                      = Symbol('△', '!'),
            log_level_error                     = Symbol('⨯', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('◌', '◍', '◎', '●'), 
                                                    ascii_symbols=('.', 'o', 'O', 'o'))
        )
    )

    FOCUS: Theme = Theme(
        active   = Style(fg_color='#2563EB'),
        submit   = Style(fg_color='#16A34A'),
        cancel   = Style(fg_color='#DC2626'),
        error    = Style(fg_color='#D97706'),
        info     = Style(fg_color='#0891B2'),
        muted    = Style(fg_color='#9CA3AF'),
        text     = Style(fg_color='#111827'),
        cursor   = Style(fg_color='#FFFFFF', bg_color='#111827'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('⊙', '>'),
            step_marker_cancel                  = Symbol('⊗', 'x'),
            step_marker_error                   = Symbol('⊖', '!'),
            step_marker_submit                  = Symbol('⊕', 'v'),
            connector_bar_start                 = Symbol('╔', '+'),
            connector_bar_vertical              = Symbol('║', '|'),
            connector_bar_end                   = Symbol('╚', '\\'),
            selection_widget_radio_active       = Symbol('⦿', '(*)'),
            selection_widget_radio_inactive     = Symbol('⭘', '( )'),
            selection_widget_checkbox_active    = Symbol('▣', '[x]'),
            selection_widget_checkbox_selected  = Symbol('▤', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('▢', '[ ]'),
            selection_widget_password_mask      = Symbol('∙', '*'),
            box_drawing_horizontal_bar          = Symbol('═', '='),
            box_drawing_top_right_corner        = Symbol('╗', '+'),
            box_drawing_left_connector          = Symbol('╠', '+'),
            box_drawing_bottom_right_corner     = Symbol('╝', '+'),
            log_level_info                      = Symbol('⊙', 'i'),
            log_level_success                   = Symbol('⊕', 'v'),
            log_level_warn                      = Symbol('⊖', '!'),
            log_level_error                     = Symbol('⊗', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('◤', '◥', '◢', '◣'), 
                                                    ascii_symbols=('<', '^', '>', 'v'))
        )
    )

    HIGH_CONTRAST: Theme = Theme(
        active   = Style(fg_color='#3B82F6'),
        submit   = Style(fg_color='#22C55E'),
        cancel   = Style(fg_color='#EF4444'),
        error    = Style(fg_color='#F59E0B'),
        info     = Style(fg_color='#06B6D4'),
        muted    = Style(fg_color='#52525B'),
        text     = Style(fg_color='#F8F9FA'),
        cursor   = Style(fg_color='#000000', bg_color='#F8F9FA'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('➜', '>'),
            step_marker_cancel                  = Symbol('✖', 'x'),
            step_marker_error                   = Symbol('▲', '!'),
            step_marker_submit                  = Symbol('✔', 'v'),
            connector_bar_start                 = Symbol('┏', '+'),
            connector_bar_vertical              = Symbol('┃', '|'),
            connector_bar_end                   = Symbol('┗', '\\'),
            selection_widget_radio_active       = Symbol('⏺', '(*)'),
            selection_widget_radio_inactive     = Symbol('⭘', '( )'),
            selection_widget_checkbox_active    = Symbol('█', '[x]'),
            selection_widget_checkbox_selected  = Symbol('▓', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('░', '[ ]'),
            selection_widget_password_mask      = Symbol('█', '*'),
            box_drawing_horizontal_bar          = Symbol('━', '-'),
            box_drawing_top_right_corner        = Symbol('┓', '+'),
            box_drawing_left_connector          = Symbol('┣', '+'),
            box_drawing_bottom_right_corner     = Symbol('┛', '+'),
            log_level_info                      = Symbol('ⓘ', 'i'),
            log_level_success                   = Symbol('✔', 'v'),
            log_level_warn                      = Symbol('▲', '!'),
            log_level_error                     = Symbol('✖', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('█', '▓', '▒', '░', '▒', '▓'), 
                                                    ascii_symbols=('#', '=', '-', ' ', '-', '='))
        )
    )

    NEBULA: Theme = Theme(
        active   = Style(fg_color='#89b4fa'),
        submit   = Style(fg_color='#a6e3a1'),
        cancel   = Style(fg_color='#f38ba8'),
        error    = Style(fg_color='#f9e2af'),
        info     = Style(fg_color='#89dceb'),
        muted    = Style(fg_color='#6c7086'),
        text     = Style(fg_color='#cdd6f4'),
        cursor   = Style(fg_color='#1e1e2e', bg_color='#89b4fa'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('❯', '>'),
            step_marker_cancel                  = Symbol('✕', 'x'),
            step_marker_error                   = Symbol('✖', '!'),
            step_marker_submit                  = Symbol('✔', 'v'),
            connector_bar_start                 = Symbol('╭', '+'),
            connector_bar_vertical              = Symbol('│', '|'),
            connector_bar_end                   = Symbol('╰', '\\'),
            selection_widget_radio_active       = Symbol('◉', '(*)'),
            selection_widget_radio_inactive     = Symbol('◯', '( )'),
            selection_widget_checkbox_active    = Symbol('☑', '[x]'),
            selection_widget_checkbox_selected  = Symbol('☒', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('☐', '[ ]'),
            selection_widget_password_mask      = Symbol('•', '*'),
            box_drawing_horizontal_bar          = Symbol('─', '-'),
            box_drawing_top_right_corner        = Symbol('╮', '+'),
            box_drawing_left_connector          = Symbol('├', '+'),
            box_drawing_bottom_right_corner     = Symbol('╯', '+'),
            log_level_info                      = Symbol('✦', 'i'),
            log_level_success                   = Symbol('✔', 'v'),
            log_level_warn                      = Symbol('▲', '!'),
            log_level_error                     = Symbol('✖', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('◜', '◝', '◞', '◟'), 
                                                    ascii_symbols=('|', '/', '-', '\\'))
        )
    )

    SEPIA: Theme = Theme(
        active   = Style(fg_color='#E5A93C'),
        submit   = Style(fg_color='#8A9A5B'),
        cancel   = Style(fg_color='#C85A32'),
        error    = Style(fg_color='#E07A5F'),
        info     = Style(fg_color='#D4A373'),
        muted    = Style(fg_color='#8C7A6B'),
        text     = Style(fg_color='#F5E6D3'),
        cursor   = Style(fg_color='#2C1D11', bg_color='#F5E6D3'),
        symbols  = Symbols(
            step_marker_active                  = Symbol('☞', '>'),
            step_marker_cancel                  = Symbol('⛌', 'x'),
            step_marker_error                   = Symbol('☡', '!'),
            step_marker_submit                  = Symbol('❦', 'v'),
            connector_bar_start                 = Symbol('╭', '+'),
            connector_bar_vertical              = Symbol('┊', '|'),
            connector_bar_end                   = Symbol('╰', '\\'),
            selection_widget_radio_active       = Symbol('✦', '(*)'),
            selection_widget_radio_inactive     = Symbol('✧', '( )'),
            selection_widget_checkbox_active    = Symbol('❖', '[x]'),
            selection_widget_checkbox_selected  = Symbol('◈', '[*]'),
            selection_widget_checkbox_inactive  = Symbol('◇', '[ ]'),
            selection_widget_password_mask      = Symbol('♦', '*'),
            box_drawing_horizontal_bar          = Symbol('┈', '-'),
            box_drawing_top_right_corner        = Symbol('╮', '+'),
            box_drawing_left_connector          = Symbol('├', '+'),
            box_drawing_bottom_right_corner     = Symbol('╯', '+'),
            log_level_info                      = Symbol('☙', 'i'),
            log_level_success                   = Symbol('⚜', 'v'),
            log_level_warn                      = Symbol('☡', '!'),
            log_level_error                     = Symbol('✢', 'x'),
            spinner                             = SpinnerSymbols(
                                                    unicode_symbols=('◴', '◵', '◶', '◷'), 
                                                    ascii_symbols=('|', '/', '-', '\\'))
        )
    )