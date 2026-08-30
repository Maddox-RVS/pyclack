from ..renderer import Text, Style
from .prompt_base import Alignment
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

def _chunkify(string: str, max_line_len: int) -> list[str]:
    '''
    Splits a string into chunks of a specified maximum line length,
    respecting existing newlines as hard breaks first.
 
    Args:
        string (str): The string to be chunked.
        max_line_len (int): The maximum length of each chunk.
 
    Returns:
        list[str]: A list of string chunks.
    '''
 
    def _chunk(string: str, max_line_len: int) -> list[str]:
        return [string[i:i+max_line_len] for i in range(0, len(string), max_line_len)]
 
    pieces: list[str] = string.split('\n')
    chunks: list[str] = []
    for piece in pieces:
        piece_chunks: list[str] = _chunk(piece, max_line_len)
        for chunk in piece_chunks: chunks.append(chunk)
    return chunks
 
def build_attached_box_lines(
    title: str,
    message: str,
    prefix: Text,
    title_marker_prefix: Text,
    title_style: Style,
    message_style: Style,
    border_style: Style,
    right_bar_symbol: str,
    horizontal_bar_symbol: str,
    left_connector_symbol: str,
    top_right_corner_symbol: str,
    bottom_right_corner_symbol: str) -> list[Text]:
    '''
    Builds a box "attached" to a connector bar on the left, in clack's
    `note()` style: the left side is just the ordinary prefix continuing
    through (no left border is drawn), the box hangs off the right side
    only, its top-right corner attaches to a horizontal bar that begins
    right after the title marker prefix, and the bottom closes with a
    left-connector T-junction rather than a full left corner.
 
    Args:
        title (str): The title text shown on the box's top line.
        message (str): The body content shown inside the box.
        prefix (Text): The ordinary left-side prefix (e.g. a muted connector bar) used for every line except the title's first line.
        title_marker_prefix (Text): The special prefix used only for the title's first line (e.g. a step marker).
        title_style (Style): Style applied to the title text.
        message_style (Style): Style applied to the message text.
        border_style (Style): Style applied to all border characters (bars, corners, connector).
        right_bar_symbol (str): The glyph used for the box's right-side vertical bar.
        horizontal_bar_symbol (str): The glyph used for horizontal bar segments.
        left_connector_symbol (str): The glyph used at the bottom-left T-junction.
        top_right_corner_symbol (str): The glyph used at the top-right corner.
        bottom_right_corner_symbol (str): The glyph used at the bottom-right corner.
 
    Returns:
        list[Text]: The fully assembled, ready-to-render lines of the box.
    '''
 
    cols, _ = shutil.get_terminal_size()
    max_chars_per_line: int = cols - (len(prefix) * 2)
    title_chunks: list[str] = _chunkify(title, max_chars_per_line)
    message_chunks: list[str] = _chunkify(message, max_chars_per_line)
    longest_line_len: int = max(len(title_chunks[-1]), max(len(line) for line in message_chunks))
 
    lines: list[Text] = []
 
    for i, chunk in enumerate(title_chunks):
        prefix_custom: Text = prefix
        if i == 0: prefix_custom = title_marker_prefix
 
        chunk_text: Text = prefix_custom + Text(chunk, title_style)
        if i == len(title_chunks) - 1:
            padding_amount: int = longest_line_len - len(chunk)
            padding_text: Text = Text(f'{horizontal_bar_symbol}' * padding_amount, border_style)
            chunk_text = Text.assemble(
                prefix_custom,
                (chunk, title_style),
                ' ',
                padding_text,
                (horizontal_bar_symbol, border_style),
                (top_right_corner_symbol, border_style))
        lines.append(chunk_text)
 
    seperator_text: Text = Text.assemble(
        prefix,
        ' ' * longest_line_len,
        (f'  {right_bar_symbol}', border_style))
    lines.append(seperator_text)
 
    for chunk in message_chunks:
        padding_amount = longest_line_len - len(chunk)
        padding_text = Text(' ' * padding_amount, message_style)
        chunk_text = Text.assemble(
            prefix,
            (chunk, message_style),
            padding_text,
            (f'  {right_bar_symbol}', border_style))
        lines.append(chunk_text)
 
    lines.append(seperator_text)
 
    bottom_line_text: Text = Text.assemble(
        (f'{left_connector_symbol}', border_style),
        (f'{horizontal_bar_symbol}' * (longest_line_len + 4), border_style),
        (f'{bottom_right_corner_symbol}', border_style))
    lines.append(bottom_line_text)
 
    return lines

def _align_line(text: str, inner_width: int, align: Alignment) -> str:
    '''
    Pads a single line of text to exactly inner_width characters, aligned
    as specified. Assumes len(text) <= inner_width (the caller is
    responsible for wrapping/chunking beforehand).
 
    Args:
        text (str): The line to pad.
        inner_width (int): The total width to pad up to.
        align (Alignment): Where the text should sit within that width.
 
    Returns:
        str: The padded line, exactly inner_width characters long.
    '''
 
    extra: int = inner_width - len(text)
    if align == Alignment.LEFT: return text + (' ' * extra)
    if align == Alignment.RIGHT: return (' ' * extra) + text
    left_pad: int = extra // 2
    right_pad: int = extra - left_pad
    return (' ' * left_pad) + text + (' ' * right_pad)
 
def build_box_lines(
    content: str,
    title: str,
    prefix: Text,
    content_style: Style,
    title_style: Style,
    border_style: Style,
    top_left_symbol: str,
    top_right_symbol: str,
    bottom_left_symbol: str,
    bottom_right_symbol: str,
    horizontal_bar_symbol: str,
    vertical_bar_symbol: str,
    content_align: Alignment = Alignment.LEFT,
    title_align: Alignment = Alignment.LEFT,
    width: int | None = None,
    title_padding: int = 1,
    content_padding: int = 2) -> list[Text]:
    '''
    Builds a fully self-contained, four-sided bordered box (clack's `box()`
    style): all four
    corners are drawn, the title sits embedded in the top border, and the
    box can either auto-size to its content or be constrained to a fixed
    total width (wrapping content that doesn't fit).
 
    Args:
        content (str): The body content shown inside the box.
        title (str): The title text embedded in the top border. Pass '' for no title.
        prefix (Text): The left-side prefix prepended to every line (e.g. a muted connector bar).
        content_style (Style): Style applied to the content text.
        title_style (Style): Style applied to the title text.
        border_style (Style): Style applied to all border characters (corners, bars, sides).
        top_left_symbol (str): Glyph for the top-left corner.
        top_right_symbol (str): Glyph for the top-right corner.
        bottom_left_symbol (str): Glyph for the bottom-left corner.
        bottom_right_symbol (str): Glyph for the bottom-right corner.
        horizontal_bar_symbol (str): Glyph used for horizontal border segments.
        vertical_bar_symbol (str): Glyph used for the left/right vertical sides.
        content_align (Alignment): Horizontal alignment of content lines within the box. Defaults to Alignment.LEFT.
        title_align (Alignment): Horizontal alignment of the title within the top border. Defaults to Alignment.LEFT.
        width (int | None): Fixed total box width (including borders), or None to auto-size to fit the content/title. Defaults to None.
        title_padding (int): Number of spaces surrounding the title text itself. Defaults to 1.
        content_padding (int): Number of spaces surrounding content lines, on each side. Defaults to 2.
 
    Returns:
        list[Text]: The fully assembled, ready-to-render lines of the box.
    '''
 
    title = title.strip()
 
    cols, _ = shutil.get_terminal_size()
    max_total_width: int = max(1, cols - len(prefix.get_raw_text()))
 
    if width is not None:
        max_content_padding: int = max(0, (width - 2 - 1) // 2)
        content_padding = min(content_padding, max_content_padding)
        max_title_padding: int = max(0, (width - 2 - 2 - 1) // 2)
        title_padding = min(title_padding, max_title_padding)
 
    title_gap: str = ' ' * title_padding if title else ''
 
    max_inner_width: int = max(1, max_total_width - (2 + content_padding * 2))
 
    if width is None:
        raw_lines: list[str] = content.split('\n')
        widest_content: int = max((len(line) for line in raw_lines), default=0)
        inner_width = min(widest_content, max_inner_width)
    else:
        total_border_and_padding: int = 2 + content_padding * 2  # left + right border chars, plus padding
        inner_width = max(1, min(width - total_border_and_padding, max_inner_width))
 
    content_lines: list[str] = []
    for raw_line in content.split('\n'):
        if len(raw_line) <= inner_width: content_lines.append(raw_line)
        else:
            content_lines.extend(
                raw_line[i:i + inner_width] for i in range(0, len(raw_line), inner_width))
 
    lines: list[Text] = []
 
    top_border_span: int = inner_width + content_padding * 2
 
    if title:
        max_title_chunk_len: int = max(1, top_border_span - title_padding * 2 - 2)
        title_lines: list[str] = [
            title[i:i + max_title_chunk_len] for i in range(0, len(title), max_title_chunk_len)
        ] or ['']
 
        for chunk in title_lines[:-1]:
            lines.append(Text.assemble(prefix, (chunk, title_style)))
 
        last_chunk: str = title_lines[-1]
        padded_last_chunk: str = f'{title_gap}{last_chunk}{title_gap}'
        available_for_bars: int = max(0, top_border_span - len(padded_last_chunk))
        if title_align == Alignment.LEFT:
            left_bars, right_bars = 1, available_for_bars - 1
        elif title_align == Alignment.RIGHT:
            left_bars, right_bars = available_for_bars - 1, 1
        else:
            left_bars = available_for_bars // 2
            right_bars = available_for_bars - left_bars
        left_bars = max(0, left_bars)
        right_bars = max(0, right_bars)
 
        top_line: Text = Text.assemble(
            prefix,
            (top_left_symbol, border_style),
            (horizontal_bar_symbol * left_bars, border_style),
            (padded_last_chunk, title_style),
            (horizontal_bar_symbol * right_bars, border_style),
            (top_right_symbol, border_style))
    else:
        top_line = Text.assemble(
            prefix,
            (top_left_symbol, border_style),
            (horizontal_bar_symbol * top_border_span, border_style),
            (top_right_symbol, border_style))
    lines.append(top_line)
 
    # Content lines
    pad_str: str = ' ' * content_padding
    for line in content_lines:
        aligned: str = _align_line(line, inner_width, content_align)
        content_line: Text = Text.assemble(
            prefix,
            (vertical_bar_symbol, border_style),
            (f'{pad_str}{aligned}{pad_str}', content_style),
            (vertical_bar_symbol, border_style))
        lines.append(content_line)
 
    # Bottom border
    bottom_span: int = inner_width + content_padding * 2
    bottom_line: Text = Text.assemble(
        prefix,
        (bottom_left_symbol, border_style),
        (horizontal_bar_symbol * bottom_span, border_style),
        (bottom_right_symbol, border_style))
    lines.append(bottom_line)
 
    return lines

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
        self.set_cursor_position(0 if new_line_index == -1 else new_line_index + 1)
 
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