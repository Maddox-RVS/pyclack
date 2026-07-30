from ..renderer import Themes, RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException
from typing import Callable, Optional, override
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy
import shutil

def ask(message: str, 
        placeholder: Optional[str] = None, 
        initial_value: Optional[str] = None, 
        validate: Optional[Callable[[str], Optional[str]]] = None,
        cancellation_message: str = 'Operation Cancelled') -> str:
    '''
    Ask the user for input with a message, placeholder, initial value, and validation function.
    '''
    
    prompt: Ask = Ask(message, cancellation_message, placeholder, initial_value, validate)
    return prompt.input_buffer

class Ask(PromptBase):
    def __init__(self,
            message: str,
            cancellation_message: str,
            placeholder: Optional[str] = None,
            initial_value: Optional[str] = None,
            validate: Optional[Callable[[str], Optional[str]]] = None):
        '''
        Initialize an Ask prompt with the given message, placeholder, initial value, and validation function.
        '''

        super().__init__()

        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.placeholder: Optional[str] = placeholder
        self.initial_value: Optional[str] = initial_value
        self.validate: Optional[Callable[[str], Optional[str]]] = validate

        self.render_frame: RenderFrame = RenderFrame()
        self.input_buffer: str = initial_value if initial_value is not None else ''
        self.input_index: int = 0 if initial_value is None else len(initial_value)
        
        self.propogate_key_after_error = True

        super().activate()

    def _build_wrapped_input_lines(self, text_style: Style, connector_bar_vertical_style: Style, show_cursor: bool = False) -> list[Text]:
        '''
        Builds the wrapped input lines based on the current input buffer and cursor position, applying the appropriate styles.
        '''

        theme: Theme = get_active_theme()
 
        connector_bar_vertical = theme.symbols.connector_bar_vertical.resolve()
        prefix_plain = f'{connector_bar_vertical}  '
        columns, _ = shutil.get_terminal_size()
        available = max(1, columns - len(prefix_plain))
 
        buffer = self.input_buffer
        idx = self.input_index
 
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

    @override
    def _handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        if not key: key = ''

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Update the input buffer based on the key pressed
        if key == 'BACKSPACE': # Remove character at input_index in input_buffer
            self.input_buffer = self.input_buffer[:max(0, self.input_index - 1)] + self.input_buffer[self.input_index:]
            self.input_index = max(0, self.input_index - 1)
        elif key == 'ENTER': return True # Advance to the next state (submit)
        elif key == 'LEFT': self.input_index = max(0, self.input_index - 1) # Move input_index once to the left
        elif key == 'RIGHT': self.input_index = min(len(self.input_buffer), self.input_index + 1) # Move input_index once to the right
        else:
            map: dict[str, str] = {
                'SPACE': ' ',
                'TAB': '\t',
                'UP': '',
                'DOWN': ''}  
            char: str = map.get(key, key)
            self.input_buffer = self.input_buffer[:self.input_index] + char + self.input_buffer[self.input_index:]
            self.input_index = min(len(self.input_buffer), self.input_index + 1)

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(
            Text(step_marker_active, 
                Text(f'  {self.message}', style=theme.text), 
            style=theme.active))
 
        if self.placeholder and len(self.input_buffer) <= 0:
            first_char: str = self.placeholder[0]
            rest_of_str: str = self.placeholder[1:]
            frame_builder.add_line(
                Text(connector_bar_vertical, 
                    Text('  ', Text(f'{first_char}', Text(f'{rest_of_str}', style=theme.muted), style=theme.cursor)),
                style=theme.active))
        else:
            for line in self._build_wrapped_input_lines(theme.text, theme.active, True):
                frame_builder.add_line(line)
 
        frame_builder.add_line(Text(connector_bar_end, style=theme.active))
 
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def _handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(
            Text(step_marker_submit, 
                Text(f'  {self.message}', style=theme.text),
            style=theme.submit))
        for line in self._build_wrapped_input_lines(theme.muted, theme.muted):
            frame_builder.add_line(line)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate(self.input_buffer) else True

    @override
    def _handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(
            Text(step_marker_error, 
                Text(f'  {self.message}', style=theme.text),
            style=theme.error))
        if self.placeholder and len(self.input_buffer) <= 0:
            first_char: str = self.placeholder[0]
            rest_of_str: str = self.placeholder[1:]
            frame_builder.add_line(
                Text(connector_bar_vertical, 
                    Text('  ', Text(f'{first_char}', Text(f'{rest_of_str}', style=theme.muted), style=theme.cursor)),
                style=theme.error))
        else:
            for line in self._build_wrapped_input_lines(theme.text, theme.error, True):
                frame_builder.add_line(line)

        frame_builder.add_line(
            Text(f'{connector_bar_end}  ', 
                Text(self.validate(self.input_buffer), style=theme.error),
            style=theme.error))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        if key == 'ENTER' or key == None: return False
        else: return True

    @override
    def _handle_cancel(self) -> None:
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(
            Text(step_marker_cancel, 
                Text(f'  {self.message}', style=theme.text),
            style=theme.cancel))
        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        if len(self.input_buffer) > 0:
            for line in self._build_wrapped_input_lines(text_style, theme.muted):
                frame_builder.add_line(line)
        frame_builder.add_line(
            Text(connector_bar_vertical, style=theme.muted))
        frame_builder.add_line(
            Text(f'{connector_bar_end}  ', 
                Text(self.cancellation_message, style=theme.cancel), 
            style=theme.muted))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, self.input_buffer)