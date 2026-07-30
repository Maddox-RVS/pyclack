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