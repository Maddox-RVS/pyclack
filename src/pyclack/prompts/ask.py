from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException
from typing import Callable, Optional, override
from ..terminal import CursorController as cc
from .util import build_wrapped_input_lines
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

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

    @override
    def handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        if not key: key = ''

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
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
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.active)
        message_lines[0] = Text(step_marker_active, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.active)
        frame_builder.add_lines(*message_lines)
 
        if self.placeholder and len(self.input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, 0, theme.muted, theme.active, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(self.input_buffer, self.input_index, theme.text, theme.active, True))
 
        frame_builder.add_line(Text(connector_bar_end, style=theme.active))
 
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] =  build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_submit, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.submit)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(self.input_buffer, self.input_index, theme.muted, theme.muted))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate(self.input_buffer) else True

    @override
    def handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.error)
        message_lines[0] = Text(step_marker_error, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.error)
        frame_builder.add_lines(*message_lines)
        if self.placeholder and len(self.input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, 0, theme.muted, theme.error, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(self.input_buffer, self.input_index, theme.text, theme.error, True))

        validation_error_message: str = self.validate(self.input_buffer)
        error_lines: list[Text] = build_wrapped_input_lines(validation_error_message, 0, theme.error, theme.error)
        last_index: int = len(error_lines) - 1
        error_lines[last_index] = Text(connector_bar_end, Text(error_lines[last_index].get_raw_text()[1:], style=theme.error), style=theme.error)
        frame_builder.add_lines(*error_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        if key == 'ENTER' or key == None: return False
        else: return True

    @override
    def handle_cancel(self) -> None:
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] =  build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_cancel, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.cancel)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        if len(self.input_buffer) > 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.input_buffer, self.input_index, text_style, theme.muted))
        frame_builder.add_line(Text(connector_bar_vertical, style=theme.muted))
        cancel_lines: list[Text] = build_wrapped_input_lines(self.cancellation_message, 0, theme.cancel, theme.muted)
        last_index: int = len(cancel_lines) - 1
        cancel_lines[last_index] = Text(connector_bar_end, Text(cancel_lines[last_index].get_raw_text()[1:], style=theme.cancel), style=theme.muted)
        frame_builder.add_lines(*cancel_lines)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, self.input_buffer)