from colorama import just_fix_windows_console

just_fix_windows_console() # Fixes Windows console for ANSI escape sequences

CSI: str = '\x1b[' # Control Sequence Introducer, prefix for all these codes

class CursorController:
    '''
    A class for controlling the cursor in the terminal. Provides methods for moving the cursor, hiding/showing the cursor, and saving/restoring the cursor position.
    '''

    @staticmethod
    def cursor_up(n: int = 1) -> str:
        '''
        Move the cursor up n lines (does not change column).

        Args:
            n (int): The number of lines to move the cursor up. Defaults to 1

        Returns:
            str: The ANSI escape sequence to move the cursor up n lines.
        '''

        if n <= 0:
            return ""
        return f"{CSI}{n}A"
 
 
    @staticmethod
    def cursor_down(n: int = 1) -> str:
        '''
        Move the cursor down n lines (does not change column).

        Args:
            n (int): The number of lines to move the cursor down. Defaults to 1

        Returns:
            str: The ANSI escape sequence to move the cursor down n lines.
        '''

        if n <= 0:
            return ""
        return f"{CSI}{n}B"
    
    @staticmethod
    def cursor_to_col(col: int = 1) -> str:
        '''
        Move the cursor to a specific column (1-indexed) on the current line.

        Args:
            col (int): The column number to move the cursor to. Defaults to 1 (the beginning of the line).

        Returns:
            str: The ANSI escape sequence to move the cursor to the specified column.
        '''

        return f"{CSI}{col}G"
    
    @staticmethod
    def clear_line() -> str:
        '''
        Clear the entire current line (cursor position on the line is unchanged).

        Returns:
            str: The ANSI escape sequence to clear the current line.
        '''

        return f"{CSI}2K"
    
    @staticmethod
    def clear_to_end_of_line() -> str:
        '''
        Clear from the cursor position to the end of the current line.

        Returns:
            str: The ANSI escape sequence to clear from the cursor position to the end of the line
        '''

        return f"{CSI}0K"
    
    @staticmethod
    def clear_below() -> str:
        '''
        Clear from the cursor position to the end of the screen.

        Returns:
            str: The ANSI escape sequence to clear from the cursor position to the end of the screen
        '''

        return f"{CSI}0J"

    @staticmethod
    def clear_screen() -> str:
        '''
        Clear the entire screen and move the cursor to the top-left (home).

        Returns:
            str: The ANSI escape sequence to clear the entire screen and move the cursor to the top
        '''
        
        return f"{CSI}2J{CSI}H"
    
    @staticmethod
    def hide_cursor() -> str:
        '''
        Hide the cursor.

        Returns:
            str: The ANSI escape sequence to hide the cursor.
        '''

        return f"{CSI}?25l"
    
    @staticmethod
    def show_cursor() -> str:
        '''
        Show the cursor.

        Returns:
            str: The ANSI escape sequence to show the cursor.
        '''

        return f"{CSI}?25h"
    
    @staticmethod
    def move_to_line_start_and_clear(n_lines_up: int = 0) -> str:
        '''
        Convenience: move up `n_lines_up` lines, then clear from there down to
        the end of the screen, and put cursor at the beginning of the line. This is the core "erase the previous frame"
        operation the redraw loop will call before printing a new frame.

        Args:
            n_lines_up (int): The number of lines to move the cursor up before clearing.

        Returns:
            str: The ANSI escape sequence to move the cursor up, clear below, and move to
        '''

        return CursorController.cursor_up(n_lines_up) + CursorController.cursor_to_col(1) + CursorController.clear_below()