from colorama import just_fix_windows_console

just_fix_windows_console()  # Fixes Windows console for ANSI escape sequences

CSI: str = '\x1b[' # Control Sequence Introducer, prefix for all these codes

class CursorController:
    '''
    A class for controlling the cursor in the terminal. Provides methods for moving the cursor, hiding/showing the cursor, and saving/restoring the cursor position.
    '''

    @staticmethod
    def cursor_up(n: int = 1) -> str:
        '''
        Move the cursor up n lines (does not change column).
        '''

        if n <= 0:
            return ""
        return f"{CSI}{n}A"
 
 
    @staticmethod
    def cursor_down(n: int = 1) -> str:
        '''
        Move the cursor down n lines (does not change column).
        '''

        if n <= 0:
            return ""
        return f"{CSI}{n}B"
    
    @staticmethod
    def cursor_to_col(col: int = 1) -> str:
        '''
        Move the cursor to a specific column (1-indexed) on the current line.
        '''

        return f"{CSI}{col}G"
    
    @staticmethod
    def clear_line() -> str:
        '''
        Clear the entire current line (cursor position on the line is unchanged).
        '''

        return f"{CSI}2K"
    
    @staticmethod
    def clear_to_end_of_line() -> str:
        '''
        Clear from the cursor position to the end of the current line.
        '''

        return f"{CSI}0K"
    
    @staticmethod
    def clear_below() -> str:
        '''
        Clear from the cursor position to the end of the screen.
        '''

        return f"{CSI}0J"

    @staticmethod
    def clear_screen() -> str:
        '''
        Clear the entire screen and move the cursor to the top-left (home).
        '''
        
        return f"{CSI}2J{CSI}H"
    
    @staticmethod
    def hide_cursor() -> str:
        '''
        Hide the cursor.
        '''

        return f"{CSI}?25l"
    
    @staticmethod
    def show_cursor() -> str:
        '''
        Show the cursor.
        '''

        return f"{CSI}?25h"
    
    @staticmethod
    def move_to_line_start_and_clear(n_lines_up: int = 0) -> str:
        '''
        Convenience: move up `n_lines_up` lines, then clear from there down to
        the end of the screen, and put cursor at the beginning of the line. This is the core "erase the previous frame"
        operation the redraw loop will call before printing a new frame.
        '''

        return CursorController.cursor_up(n_lines_up) + CursorController.cursor_to_col(1) + CursorController.clear_below()