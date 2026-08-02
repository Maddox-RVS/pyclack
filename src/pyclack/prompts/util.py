from ..renderer import Theme, Text, Style
from ..config import get_active_theme
from typing import Optional
import shutil

def splitlines(text: str, index: int) -> tuple[list[str], int, int]:
    '''
    Splits the given text into lines and returns the line and character index of the given index.

    Args:
        text (str): The text to split.
        index (int): The index to find the line and character index for.

    Returns:
        tuple[list[str], int, int]: A tuple containing the lines, line index, and character index.
    '''

    index = max(0, min(index, len(text)))
    lines = text.split('\n')
    current_pos = 0
    line_index = 0
    char_index = 0
    for i, line in enumerate(lines):
        line_length = len(line)
        if current_pos <= index <= current_pos + line_length:
            line_index = i
            char_index = index - current_pos
            break
        current_pos += line_length + 1
    return lines, line_index, char_index

def build_wrapped_input_lines(
        text: str, 
        prefix: str,
        cursor_index: int, 
        text_style: Style,
        prefix_style: Style, 
        show_cursor: bool = False) -> list[Text]:
    '''
    Builds the wrapped input lines based on the given text, prefix, cursor index, text style, and prefix style. It also takes into account whether to show the cursor or not.

    Args:
        text (str): The input text to be wrapped.
        prefix (str): The prefix to be added to each line of the wrapped input.
        cursor_index (int): The index of the cursor in the input text.
        text_style (Style): The style to be applied to the input text.
        prefix_style (Style): The style to be applied to the prefix.
        show_cursor (bool): Whether to show the cursor or not. Defaults to False.

    Returns:
        list[Text]: A list of Text objects representing the wrapped input lines.
    '''

    def wrapping_logic(text: str, 
                       prefix: str,
                       cursor_index: int, 
                       text_style: Style, 
                       prefix_style: Style, 
                       show_cursor: bool) -> list[Text]:
        theme: Theme = get_active_theme()

        columns, _ = shutil.get_terminal_size()
        available = max(1, columns - len(prefix))

        buffer = text
        idx = cursor_index

        chunks = [buffer[i:i + available] for i in range(0, len(buffer), available)] or ['']

        lines: list[Text] = []
        consumed = 0
        for chunk in chunks:
            chunk_start = consumed
            chunk_end = consumed + len(chunk)
            consumed = chunk_end

            cursor_in_chunk = chunk_start <= idx < chunk_end
            cursor_at_buffer_end_in_chunk = (idx == chunk_end == len(buffer))

            if cursor_in_chunk or cursor_at_buffer_end_in_chunk:
                local_idx = idx - chunk_start
                first = chunk[:local_idx]
                middle = chunk[local_idx:local_idx + 1]
                rest = chunk[local_idx + 1:]
                if len(middle) == 0: middle = ' '
                content = Text.assemble(
                    (first, text_style),
                    (middle, theme.cursor if show_cursor else text_style),
                    (rest, text_style))
            else:
                content = Text(chunk, text_style)

            lines.append(Text(prefix, prefix_style) + content)

        return lines

    text_lines, cursor_text_line, cursor_col_index = splitlines(text, cursor_index)
    wrapped_input_lines: list[Text] = []
    for i, text_line in enumerate(text_lines):
        if i == cursor_text_line and show_cursor: wrapped_input_lines += wrapping_logic(text_line, prefix, cursor_col_index, text_style, prefix_style, True)
        else: wrapped_input_lines += wrapping_logic(text_line, prefix, 0, text_style, prefix_style, False)
    return wrapped_input_lines

class TextBoxController:
    '''
    A class to manage the input buffer and cursor position for a text box. It provides methods to manipulate the 
    input buffer and cursor position, including moving the cursor, inserting text, and deleting text.
    '''

    def __init__(self):
        '''
        Initialize a TextBoxController with an empty input buffer and the cursor at the start of the buffer.
        '''

        self._input_buffer: str = ''
        self._cursor_index: int = 0
        self._desired_line_position: Optional[int] = None

    def _get_cursor_line_position(self) -> int:
        '''
        Get the position of the cursor within the current line.

        Returns:
            int: The position of the cursor within the current line.
        '''

        previous_newline = self._input_buffer.rfind('\n', 0, self._cursor_index)
        if previous_newline == -1:
            return self._cursor_index
        return self._cursor_index - (previous_newline + 1)

    def set_input(self, input_buffer: str, input_index: int) -> None:
        '''
        Set the input buffer and cursor position.

        Args:
            input_buffer (str): The new input buffer.
            input_index (int): The new cursor position.

        Raises:
            ValueError: If the input_index is outside the bounds of the input buffer.
        '''

        if input_index < 0 or input_index > len(input_buffer):
            raise ValueError("input_index must be within the bounds of input_buffer")

        self._input_buffer = input_buffer
        self.set_cursor_position(input_index)

    def get_input(self) -> str:
        '''
        Get the current input buffer.

        Returns:
            str: The current input buffer.
        '''

        return self._input_buffer

    def clear_input(self) -> None:
        '''
        Clear the input buffer and reset the cursor to the start of the buffer.
        '''

        self._input_buffer = ''
        self.set_cursor_position(0)

    def set_cursor_position(self, position: int) -> None:
        '''
        Set the cursor position.

        Args:
            position (int): The new cursor position.

        Raises:
            ValueError: If the position is outside the bounds of the input buffer.
        '''

        if position < 0 or position > len(self._input_buffer):
            raise ValueError("position must be within the bounds of input_buffer")
        self._cursor_index = position

    def get_cursor_position(self) -> int:
        '''
        Get the current cursor position.

        Returns:
            int: The current cursor position.
        '''

        return self._cursor_index

    def cursor_home(self) -> None:
        '''
        Move the cursor to the beginning of the input buffer.
        '''

        self.set_cursor_position(0)

    def cursor_end(self) -> None:
        '''
        Move the cursor to the end of the input buffer.
        '''

        self.set_cursor_position(len(self._input_buffer))

    def cursor_line_home(self) -> None:
        '''
        Move the cursor to the beginning of the current line.
        '''
        
        new_line_index: int = self._input_buffer.rfind('\n', 0, self._cursor_index)
        self.set_cursor_position(new_line_index)

    def is_cursor_home(self) -> bool:
        '''
        Check if the cursor is at the beginning of the input buffer.

        Returns:
            bool: True if the cursor is at the beginning of the input buffer, False otherwise.
        '''

        return self._cursor_index == 0

    def is_cursor_end(self) -> bool:
        '''
        Check if the cursor is at the end of the input buffer.

        Returns:
            bool: True if the cursor is at the end of the input buffer, False otherwise.
        '''

        return self._cursor_index == len(self._input_buffer)

    def is_cursor_line_home(self) -> bool:
        '''
        Check if the cursor is at the beginning of the current line.

        Returns:
            bool: True if the cursor is at the beginning of the current line, False otherwise.
        '''

        new_line_index: int = self._input_buffer.rfind('\n', 0, self._cursor_index)
        if new_line_index == -1: return self._cursor_index == 0
        else: return self._cursor_index == new_line_index + 1

    def cursor_left(self, steps: int = 1) -> None:
        '''
        Move the cursor to the left by a specified number of steps.

        Args:
            steps (int): The number of steps to move the cursor left. Must be a non-negative integer.

        Raises:
            ValueError: If steps is a negative integer.
        '''

        self.set_cursor_position(max(0, self._cursor_index - steps))

    def cursor_right(self, steps: int = 1) -> None:
        '''
        Move the cursor to the right by a specified number of steps.

        Args:
            steps (int): The number of steps to move the cursor right. Must be a non-negative integer.

        Raises:
            ValueError: If steps is a negative integer.
        '''

        self.set_cursor_position(min(len(self._input_buffer), self._cursor_index + steps))

    def cursor_up(self, steps: int = 1) -> None:
        '''
        Move the cursor up by a specified number of lines, maintaining the desired horizontal position.

        Args:
            steps (int): The number of lines to move the cursor up. Must be a non-negative integer.

        Raises:
            ValueError: If steps is a negative integer.
        '''

        if steps < 0: raise ValueError("steps must be a non-negative integer")
        elif steps == 0 or self._cursor_index == 0: return

        if self._desired_line_position is None:
            self._desired_line_position = self._get_cursor_line_position()

        previous_newline = self._input_buffer.rfind('\n', 0, self._cursor_index)
        if previous_newline == -1: return  # Already on top line

        current_line_end = previous_newline
        target_line_start = 0
        target_line_end = 0

        for _ in range(steps):
            if current_line_end == -1: break
            prev = self._input_buffer.rfind('\n', 0, current_line_end)
            target_line_start = 0 if prev == -1 else prev + 1
            target_line_end = current_line_end
            current_line_end = prev

        target_line_length = target_line_end - target_line_start
        new_position = target_line_start + min(self._desired_line_position, target_line_length)

        self.set_cursor_position(new_position)

    def cursor_down(self, steps: int = 1) -> None:
        '''
        Move the cursor down by a specified number of lines, maintaining the desired horizontal position.

        Args:
            steps (int): The number of lines to move the cursor down. Must be a non-negative integer.

        Raises:
            ValueError: If steps is a negative integer.
        '''

        if steps < 0: raise ValueError("steps must be a non-negative integer")
        elif steps == 0: return

        if self._desired_line_position is None:
            self._desired_line_position = self._get_cursor_line_position()

        next_newline = self._input_buffer.find('\n', self._cursor_index)
        if next_newline == -1: return  # Already on bottom line

        current_line_start = next_newline + 1
        target_line_start = current_line_start
        target_line_end = len(self._input_buffer)

        for _ in range(steps):
            next_line_end = self._input_buffer.find('\n', current_line_start)
            if next_line_end == -1:
                target_line_start = current_line_start
                target_line_end = len(self._input_buffer)
                break
            target_line_start = current_line_start
            target_line_end = next_line_end
            current_line_start = next_line_end + 1

        target_line_length = target_line_end - target_line_start
        new_position = target_line_start + min(self._desired_line_position, target_line_length)

        self.set_cursor_position(new_position)

    def insert(self, text: str) -> None:
        '''
        Insert text at the current cursor position in the input buffer.

        Args:
            text (str): The text to insert.
        '''

        self._input_buffer = self._input_buffer[:self._cursor_index] + text + self._input_buffer[self._cursor_index:]
        self.cursor_right(len(text))

    def delete(self, steps: int = 1) -> None:
        '''
        Delete a specified number of characters to the left of the cursor in the input buffer.

        Args:
            steps (int): The number of characters to delete. Must be a non-negative integer.

        Raises:
            ValueError: If steps is a negative integer.
        '''

        if steps < 0: raise ValueError("steps must be a non-negative integer")
        elif steps == 0: return
        self._input_buffer = self._input_buffer[:max(0, self._cursor_index - steps)] + self._input_buffer[self._cursor_index:]
        self.cursor_left(steps)

    def __str__(self) -> str:
        visual_cursor_left = '>>>'
        visual_cursor_right = '<<<'

        def highlight_index(text: str, index: int) -> str:
            if not text:
                return ">>> <<<"

            # Clamp index to a valid character position in the string
            index = max(0, min(index, len(text) - 1))

            return text[:index] + ">>>" + text[index] + "<<<" + text[index + 1 :]
        
        return (
            f'Input Buffer: "{self._input_buffer}"\n'
            f'Cursor Index: {self._cursor_index}\n'
            f'Visual Representation: \n{highlight_index(self._input_buffer, self._cursor_index)}'
        )

    def __repr__(self) -> str:
        return f'TextBoxController(input_buffer="{self._input_buffer}", cursor_index={self._cursor_index})'