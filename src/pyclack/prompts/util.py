from ..renderer import Text, Style
import shutil

def build_message_open(
    message: str,
    message_style: Style,
    prefix: Text,
    opening_prefix: Text) -> list[Text]:
    '''
    Constructs a list of Text objects representing the opening section of a message.
    
    Args:
        message (str): The primary content message text.
        message_style (Style): Style applied to the main message body.
        prefix (Text): A general prefix for wrapping the lines.
        opening_prefix (Text): Specific prefix added to the beginning of the first line.

    Returns:
        list[Text]: List of Text objects representing the formatted opening lines.
    '''

    message = message if not message_style.bg_color else f' {message} '
    message_text: Text = Text(message, message_style)
    message_lines: list[Text] = build_wrapped_lines(message_text, prefix)
    message_lines[0] = opening_prefix + Text(message_lines[0].get_raw_text()[len(prefix):], message_style)
    return message_lines

def build_message_header(
    message: str,
    message_style: Style,
    step_marker_prefix: str,
    step_marker_prefix_style: Style,
    prefix: Text) -> list[Text]:
    '''
    Constructs a list of Text objects representing a step header in a message.
    
    Args:
        message (str): The primary content message text.
        message_style (Style): Style applied to the main message body.
        step_marker_prefix (str): Static prefix string for the step marker.
        step_marker_prefix_style (Style): Style for the static step marker prefix text.
        prefix (Text): A general prefix for wrapping the lines.

    Returns:
        list[Text]: List of Text objects representing the formatted header lines.
    '''

    message = message if not message_style.bg_color else f' {message} '
    message_text: Text = Text(message, message_style)
    step_marker_prefix_text: Text = Text(step_marker_prefix, step_marker_prefix_style)
    message_lines: list[Text] = build_wrapped_lines(message_text, prefix)
    message_lines[0] = step_marker_prefix_text + Text(message_lines[0].get_raw_text()[len(prefix):], message_style) 
    return message_lines

def build_message_close(
    message: str,
    message_style: Style,
    prefix: Text,
    closing_prefix: Text) -> list[Text]:
    '''
    Constructs a list of Text objects representing the closing section of a message.
    
    Args:
        message (str): The primary content message text.
        message_style (Style): Style applied to the main message body.
        prefix (Text): A general prefix for wrapping the lines.
        closing_prefix (Text): Specific prefix added to the end of the last line.

    Returns:
        list[Text]: List of Text objects representing the formatted closing lines.
    '''

    message = message if not message_style.bg_color else f' {message} '
    message_text: Text = Text(message, message_style)
    message_lines: list[Text] = build_wrapped_lines(message_text, prefix)
    last_index: int = len(message_lines) - 1
    message_lines[last_index] = closing_prefix + Text(message_lines[last_index].get_raw_text()[len(prefix):], message_style)
    return message_lines

def _flatten_runs(value: Text) -> list[tuple[str, Style | None]]:
    '''
    Walks a (possibly deeply nested) Text object's inner_text chain and
    returns a flat list of (raw_text, style) runs in order.

    Args:
        value (Text): The input Text object to flatten.
    
    Returns:
        list[tuple[str, Style | None]]: A list where each tuple contains the (raw text segment, applied style).
    '''

    runs: list[tuple[str, Style | None]] = []
    current: Text | None = value
    while current is not None:
        runs.append((current.get_raw_isolated_text(), current.style))
        current = current.inner_text
    return runs

def _build_slice(runs: list[tuple[str, Style | None]], start: int, end: int) -> Text:
    '''
    Rebuilds a Text spanning [start, end) of a flattened raw text,
    preserving each run's original style (or lack thereof) for whatever
    portion of it falls inside that range.

    Args:
        runs (list[tuple[str, Style | None]]): The list of all flattened runs from _flatten_runs.
        start (int): The starting character index (inclusive) for the slice.
        end (int): The ending character index (exclusive) for the slice.

    Returns:
        Text: A new Text object representing the sliced portion, preserving styles.
    '''

    if start >= end: return Text('')

    parts = []
    current_pos = 0
    for run_text, run_style in runs:
        run_end = current_pos + len(run_text)
        overlap_start = max(start, current_pos)
        overlap_end = min(end, run_end)
        if overlap_start < overlap_end:
            segment = run_text[overlap_start - current_pos:overlap_end - current_pos]
            if run_style is None: parts.append(segment)
            else: parts.append((segment, run_style))
        current_pos = run_end
        if current_pos >= end: break

    return Text.assemble(*parts) if parts else Text('')

def apply_cursor_style(text: Text, index: int, style: Style) -> Text:
    '''
    Returns a copy of the given Text with the single character at `index`
    restyled to `style`, leaving every other character's original styling
    (including deeply nested styles) untouched. Works on any Text structure
    regardless of nesting depth, since it flattens to raw runs first.
 
    If `index` lands exactly at the end of the text (i.e. there's no
    character there yet, as when a cursor sits past the last typed
    character), a single styled space is inserted to represent the cursor.
 
    Args:
        text (Text): The text to apply the cursor style to.
        index (int): The character index to style (clamped to valid range).
        style (Style): The style to apply at that index.
 
    Returns:
        Text: A new Text with the cursor style applied at that index.
    '''
 
    raw_text = text.get_raw_text()
    index = max(0, min(index, len(raw_text)))
    runs = _flatten_runs(text)
 
    first = _build_slice(runs, 0, index)
    middle_char = raw_text[index:index + 1]
 
    is_newline = middle_char == '\n'
    if middle_char == '' or is_newline:
        middle = Text(' ', style)
        rest_start = index  # don't consume the real newline just insert before it
    else:
        middle = Text(middle_char, style)
        rest_start = index + 1
 
    rest = _build_slice(runs, rest_start, len(raw_text))
 
    return first + middle + rest

def build_wrapped_lines(text: Text, prefix: Text) -> list[Text]:
    '''
    Wraps the given Text into terminal-width-limited lines, each prefixed
    with the given prefix Text, preserving the original styling (including
    deeply nested styles) across wrap boundaries.

    Args:
        text (Text): The source text content to be wrapped.
        prefix (Text): The text that should prepend every line.

    Returns:
        list[Text]: A list of Text objects, each representing a wrapped and prefixed line.
    '''

    def clone_text(value: Text) -> Text:
        if value.inner_text is None:
            return Text(value.get_raw_isolated_text(), value.style)
        return Text(value.get_raw_isolated_text(), value.style, clone_text(value.inner_text))

    raw_text = text.get_raw_text()
    runs = _flatten_runs(text)
    columns, _ = shutil.get_terminal_size()
    available = max(1, columns - len(prefix.get_raw_text()))
    wrapped: list[Text] = []

    line_start = 0
    for line in raw_text.split('\n'):
        line_len = len(line)
        line_end = line_start + line_len
        segments = max(1, (line_len + available - 1) // available)

        for i in range(segments):
            seg_start = i * available
            seg_end = min(seg_start + available, line_len)
            abs_seg_start = line_start + seg_start
            abs_seg_end = line_start + seg_end
            content = _build_slice(runs, abs_seg_start, abs_seg_end)
            wrapped.append(clone_text(prefix) + content)

        line_start = line_end + 1

    return wrapped

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
        self._desired_line_position: int | None = None
 
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
 
        self._desired_line_position = None
        self.set_cursor_position(0)
 
    def cursor_end(self) -> None:
        '''
        Move the cursor to the end of the input buffer.
        '''
 
        self._desired_line_position = None
        self.set_cursor_position(len(self._input_buffer))
 
    def cursor_line_home(self) -> None:
        '''
        Move the cursor to the beginning of the current line.
        '''
        
        self._desired_line_position = None
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
 
        self._desired_line_position = None
        self.set_cursor_position(max(0, self._cursor_index - steps))
 
    def cursor_right(self, steps: int = 1) -> None:
        '''
        Move the cursor to the right by a specified number of steps.
 
        Args:
            steps (int): The number of steps to move the cursor right. Must be a non-negative integer.
 
        Raises:
            ValueError: If steps is a negative integer.
        '''
 
        self._desired_line_position = None
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
        self._desired_line_position = None
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
        self._desired_line_position = None
        self.cursor_left(steps)
 
    def __str__(self) -> str:
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