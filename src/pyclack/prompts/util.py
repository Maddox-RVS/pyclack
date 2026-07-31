from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..config import get_active_theme
import shutil

def build_wrapped_input_lines(text: str, cursor_index: int, text_style: Style, connector_bar_vertical_style: Style, show_cursor: bool = False) -> list[Text]:
        '''
        Builds the wrapped input lines based on the given text, cursor index, text style, and connector bar vertical style. It also takes into account whether to show the cursor or not.

        Args:
            text (str): The input text to be wrapped.
            cursor_index (int): The index of the cursor in the input text.
            text_style (Style): The style to be applied to the input text.
            connector_bar_vertical_style (Style): The style to be applied to the connector bar vertical.
            show_cursor (bool): Whether to show the cursor or not. Defaults to False.
        '''

        def splitlines(text: str, index: int):
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

        def wrapping_logic(text: str, cursor_index: int, text_style: Style, connector_bar_vertical_style: Style, show_cursor: bool) -> list[Text]:
            theme: Theme = get_active_theme()
    
            connector_bar_vertical = theme.symbols.connector_bar_vertical.resolve()
            prefix_plain = f'{connector_bar_vertical}  '
            columns, _ = shutil.get_terminal_size()
            available = max(1, columns - len(prefix_plain))
    
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
                    if len(middle) == 0:
                        middle = ' '
                    content = Text(first, Text(middle, Text(rest, style=text_style), style=theme.cursor if show_cursor else text_style), style=text_style)
                else:
                    content = Text(chunk, style=text_style)
    
                lines.append(Text(connector_bar_vertical, Text('  ', content, style=theme.text), style=connector_bar_vertical_style))
    
            return lines

        text_lines, cursor_text_line, cursor_col_index = splitlines(text, cursor_index)
        wrapped_input_lines: list[Text] = []
        for i, text_line in enumerate(text_lines):
            if i == cursor_text_line and show_cursor: wrapped_input_lines += wrapping_logic(text_line, cursor_col_index, text_style, connector_bar_vertical_style, True)
            else: wrapped_input_lines += wrapping_logic(text_line, 0, text_style, connector_bar_vertical_style, False)
        return wrapped_input_lines

class TextBoxController:
    def __init__(self):
        self.input_buffer: str = ''
        self.input_index: int = 0

    def set_input(self, input_buffer: str, input_index: int) -> None:
        if input_index < 0 or input_index > len(input_buffer):
            raise ValueError("input_index must be within the bounds of input_buffer")

        self.input_buffer = input_buffer
        self.input_index = input_index

    def get_input(self) -> tuple[str, int]:
        return self.input_buffer, self.input_index

    def cursor_left(self, steps: int = 1) -> None:
        self.input_index = max(0, self.input_index - steps)

    def cursor_right(self, steps: int = 1) -> None:
        self.input_index = min(len(self.input_buffer), self.input_index + steps)

    def insert(self, text: str) -> None:
        self.input_buffer = self.input_buffer[:self.input_index] + text + self.input_buffer[self.input_index:]
        self.cursor_right(len(text))