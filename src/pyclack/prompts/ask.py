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
    Controls are as follows:
    - Use the arrow keys to move the cursor within the input.
    - Press 'Enter' to submit the input.

    Args:
        message (str): The message to display to the user.
        placeholder (str, optional): The placeholder text to display when the input is empty.
        initial_value (str, optional): The initial value of the input.
        validate (Callable[[str], Optional[str]], optional): A function to validate the input.
        cancellation_message (str): The message to display if the user cancels the operation.

    Returns:
        str: The user's input.

    Raises:
        CancelException: If the user cancels the operation.
    '''
    
    prompt: Ask = Ask(message, cancellation_message, placeholder, initial_value, validate)
    return prompt.text_box_controller.get_input()

class Ask(PromptBase):
    '''
    A prompt for asking the user for text input.
    '''

    def __init__(self,
            message: str,
            cancellation_message: str,
            placeholder: Optional[str] = None,
            initial_value: Optional[str] = None,
            validate: Optional[Callable[[str], Optional[str]]] = None):
        '''
        Initialize an Ask prompt with the given message, placeholder, initial value, and validation function.

        Args:
            message (str): The message to display to the user.
            cancellation_message (str): The message to display if the user cancels the operation.
            placeholder (str, optional): The placeholder text to display when the input is empty.
            initial_value (str, optional): The initial value of the input.
            validate (Callable[[str], Optional[str]], optional): A function to validate the input.

        Raises:
            CancelException: If the user cancels the operation.
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
        Construct a tuple of allowed inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        allowed_chars: tuple[str] = tuple(chr(i) for i in range(32, 127))
        return ('BACKSPACE', 'ENTER', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'TAB', 'SPACE') + allowed_chars

    @override
    def handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        if key not in self.allowed_inputs: key = ''

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix: str = f'{connector_bar_vertical}  '

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

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.active)
        message_lines[0] = Text(step_marker_active, theme.active) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)
 
        if self.placeholder and len(input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, prefix, 0, theme.muted, theme.active, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, prefix, input_index, theme.text, theme.active, True))
 
        frame_builder.add_line(Text(connector_bar_end, theme.active))
 
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix: str = f'{connector_bar_vertical}  '

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))
        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_submit, theme.submit) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, prefix, input_index, theme.muted, theme.muted))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate and self.validate(input_buffer) else True

    @override
    def handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix: str = f'{connector_bar_vertical}  '

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))
        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.error)
        message_lines[0] = Text(step_marker_error, theme.error) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)
        if self.placeholder and len(input_buffer) <= 0:
            frame_builder.add_lines(*build_wrapped_input_lines(self.placeholder, prefix, 0, theme.muted, theme.error, True))
        else:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, prefix, input_index, theme.text, theme.error, True))

        validation_error_message: str = self.validate(input_buffer) # self.validate must be defined if we are in the error state
        error_lines: list[Text] = build_wrapped_input_lines(validation_error_message, prefix, 0, theme.error, theme.error)
        last_index: int = len(error_lines) - 1
        error_lines[last_index] = Text(connector_bar_end, theme.error) + '  ' + Text(error_lines[last_index].get_raw_text()[3:], theme.error)
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
        prefix: str = f'{connector_bar_vertical}  '

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] =  build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_cancel, theme.cancel) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        if len(input_buffer) > 0:
            frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, prefix, input_index, text_style, theme.muted))
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))
        cancel_lines: list[Text] = build_wrapped_input_lines(self.cancellation_message, prefix, 0, theme.cancel, theme.muted)
        last_index: int = len(cancel_lines) - 1
        cancel_lines[last_index] = Text(connector_bar_end, theme.muted) + '  ' + Text(cancel_lines[last_index].get_raw_text()[3:], theme.cancel)
        frame_builder.add_lines(*cancel_lines)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, input_buffer)