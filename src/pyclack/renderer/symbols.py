class SpinnerSymbols:
    '''
    A class to represent spinner symbols for animations. It holds both Unicode and ASCII representations of the spinner symbols.
    ASCII symbols are used as a fallback for environments that do not support Unicode characters.
    '''

    def __init__(self, unicode_symbols: tuple[str], ascii_symbols: tuple[str]):
        '''
        Initialize a SpinnerSymbols object with the given Unicode and ASCII symbols.

        Args:
            unicode_symbols (tuple[str]): A tuple of Unicode symbols for the spinner.
            ascii_symbols (tuple[str]): A tuple of ASCII symbols for the spinner.
        '''
        
        self.unicode_symbols = unicode_symbols
        self.ascii_symbols = ascii_symbols 

    def get_symbols(self, use_unicode: bool = True) -> tuple[str]:
        '''
        Get the symbols based on the use_unicode flag.

        Args:
            use_unicode (bool): Whether to use Unicode symbols.

        Returns:
            tuple[str]: A tuple of symbols.
        '''

        return self.unicode_symbols if use_unicode else self.ascii_symbols

class Symbol:
    '''
    A class to represent a symbol with both Unicode and ASCII representations. It provides a method 
    to retrieve the appropriate symbol based on the environment's capabilities. Ascii symbols are used 
    as a fallback for environments that do not support Unicode characters.
    '''

    def __init__(self, unicode_symbol: str, ascii_symbol: str):
        '''
        Initialize a Symbol object with the given Unicode and ASCII symbols.

        Args:
            unicode_symbol (str): The Unicode representation of the symbol.
            ascii_symbol (str): The ASCII representation of the symbol.
        '''

        self.unicode_symbol = unicode_symbol
        self.ascii_symbol = ascii_symbol

    def get_symbol(self, use_unicode: bool = True) -> str:
        '''
        Get the symbol based on the use_unicode flag.

        Args:
            use_unicode (bool): Whether to use Unicode symbols.

        Returns:
            str: The appropriate symbol.
        '''

        return self.unicode_symbol if use_unicode else self.ascii_symbol

class Symbols:
    '''
    A class to represent a collection of symbols.
    '''

    def __init__(self,
        step_marker_active: Symbol,
        step_marker_cancel: Symbol,
        step_marker_error: Symbol,
        step_marker_submit: Symbol,
        connector_bar_start: Symbol,
        connector_bar_vertical: Symbol,
        connector_bar_end: Symbol,
        selection_widget_radio_active: Symbol,
        selection_widget_radio_inactive: Symbol,
        selection_widget_checkbox_active: Symbol,
        selection_widget_checkbox_selected: Symbol,
        selection_widget_checkbox_inactive: Symbol,
        selection_widget_password_mask: Symbol,
        box_drawing_horizontal_bar: Symbol,
        box_drawing_top_right_corner: Symbol,
        box_drawing_left_connector: Symbol,
        box_drawing_bottom_right_corner: Symbol,
        log_level_info: Symbol,
        log_level_success: Symbol,
        log_level_warn: Symbol,
        log_level_error: Symbol,
        spinner: SpinnerSymbols):
        '''
        Initialize a Symbols object with the given symbols.

        Args:
            step_marker_active (Symbol): Symbol for active step marker.
            step_marker_cancel (Symbol): Symbol for cancel step marker.
            step_marker_error (Symbol): Symbol for error step marker.
            step_marker_submit (Symbol): Symbol for submit step marker.
            connector_bar_start (Symbol): Symbol for the start of a connector bar.
            connector_bar_vertical (Symbol): Symbol for vertical connector bar.
            connector_bar_end (Symbol): Symbol for the end of a connector bar.
            selection_widget_radio_active (Symbol): Symbol for active radio button.
            selection_widget_radio_inactive (Symbol): Symbol for inactive radio button.
            selection_widget_checkbox_active (Symbol): Symbol for active checkbox.
            selection_widget_checkbox_selected (Symbol): Symbol for selected checkbox.
            selection_widget_checkbox_inactive (Symbol): Symbol for inactive checkbox.
            selection_widget_password_mask (Symbol): Symbol for password mask in selection widget.
            box_drawing_horizontal_bar (Symbol): Symbol for horizontal box drawing bar.
            box_drawing_top_right_corner (Symbol): Symbol for top right corner of box drawing.
            box_drawing_left_connector (Symbol): Symbol for left connector in box drawing.
            box_drawing_bottom_right_corner (Symbol): Symbol for bottom right corner of box drawing.
            log_level_info (Symbol): Symbol for info log level.
            log_level_success (Symbol): Symbol for success log level.
            log_level_warn (Symbol): Symbol for warning log level.
            log_level_error (Symbol): Symbol for error log level.
            spinner (SpinnerSymbols): Symbols to use for spinner animations.
        '''

        self.step_marker_active: Symbol = step_marker_active
        self.step_marker_cancel: Symbol = step_marker_cancel
        self.step_marker_error: Symbol = step_marker_error
        self.step_marker_submit: Symbol = step_marker_submit
        self.connector_bar_start: Symbol = connector_bar_start
        self.connector_bar_vertical: Symbol = connector_bar_vertical
        self.connector_bar_end: Symbol = connector_bar_end
        self.selection_widget_radio_active: Symbol = selection_widget_radio_active
        self.selection_widget_radio_inactive: Symbol = selection_widget_radio_inactive
        self.selection_widget_checkbox_active: Symbol = selection_widget_checkbox_active
        self.selection_widget_checkbox_selected: Symbol = selection_widget_checkbox_selected
        self.selection_widget_checkbox_inactive: Symbol = selection_widget_checkbox_inactive
        self.selection_widget_password_mask: Symbol = selection_widget_password_mask
        self.box_drawing_horizontal_bar: Symbol = box_drawing_horizontal_bar
        self.box_drawing_top_right_corner: Symbol = box_drawing_top_right_corner
        self.box_drawing_left_connector: Symbol = box_drawing_left_connector
        self.box_drawing_bottom_right_corner: Symbol = box_drawing_bottom_right_corner
        self.log_level_info: Symbol = log_level_info
        self.log_level_success: Symbol = log_level_success
        self.log_level_warn: Symbol = log_level_warn
        self.log_level_error: Symbol = log_level_error
        self.spinner: SpinnerSymbols = spinner