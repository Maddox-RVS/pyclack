from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .util import build_wrapped_input_lines, TextBoxController
from .prompt_base import PromptBase, CancelException
from typing import Callable, Optional, override
from ..terminal import CursorController as cc
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
    return prompt.text_box_controller.get_input()

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
        self.text_box_controller: TextBoxController = TextBoxController()
        if initial_value: 
            self.text_box_controller.set_input(initial_value, 0)
            self.text_box_controller.cursor_end()
        
        self.propogate_key_after_error = True
        self.allowed_inputs: tuple[str] = self._construct_allowed_inputs()

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str]:
        '''
        Construct a list of allowed inputs for the prompt.
        '''

        allowed_chars: tuple[str] = tuple(chr(i) for i in range(32, 127))
        return ('BACKSPACE', 'ENTER', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'TAB', 'SPACE') + allowed_chars

    @override
    def handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        if key not in self.allowed_inputs: key = ''

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Update the input buffer based on the key pressed
        if key == 'BACKSPACE': self.text_box_controller.delete()
        elif key == 'ENTER': return True # Advance to the next state (submit)
        elif key == 'LEFT': self.text_box_controller.cursor_left()
        elif key == 'RIGHT': self.text_box_controller.cursor_right()
        elif key == 'UP': self.text_box_controller.cursor_up()
        elif key == 'DOWN': self.text_box_controller.cursor_down()
        else:
            map: dict[str, str] = {
                'SPACE': ' ',
                'TAB': '\t'}  
            char: str = map.get(key, key) # Translate key to character (if applicable)
            if key != '': self.text_box_controller.insert(char)

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.active)
        message_lines[0] = Text(step_marker_active, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.active)
        frame_builder.add_lines(*message_lines)
 
        if self.placeholder and len(input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, 0, theme.muted, theme.active, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.text, theme.active, True))
 
        frame_builder.add_line(Text(connector_bar_end, style=theme.active))
 
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()

        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] =  build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_submit, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.submit)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.muted, theme.muted))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate(input_buffer) else True

    @override
    def handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.error)
        message_lines[0] = Text(step_marker_error, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.error)
        frame_builder.add_lines(*message_lines)
        if self.placeholder and len(input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, 0, theme.muted, theme.error, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.text, theme.error, True))

        validation_error_message: str = self.validate(input_buffer)
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

        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] =  build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_cancel, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.cancel)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        if len(input_buffer) > 0:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, text_style, theme.muted))
        frame_builder.add_line(Text(connector_bar_vertical, style=theme.muted))
        cancel_lines: list[Text] = build_wrapped_input_lines(self.cancellation_message, 0, theme.cancel, theme.muted)
        last_index: int = len(cancel_lines) - 1
        cancel_lines[last_index] = Text(connector_bar_end, Text(cancel_lines[last_index].get_raw_text()[1:], style=theme.cancel), style=theme.muted)
        frame_builder.add_lines(*cancel_lines)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, input_buffer)