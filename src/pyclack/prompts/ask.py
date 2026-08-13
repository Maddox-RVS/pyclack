from .util import build_wrapped_lines, build_message_header, build_message_close, apply_cursor_style, TextBoxController
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
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
        default_value: Optional[str] = None,
        cancellation_message: str = 'Operation Cancelled') -> str:
    '''
    Ask the user for input with a message, placeholder, initial value, and validation function.
    Controls are as follows:
    - Use the arrow keys to move the cursor within the input.
    - Press 'Enter' to submit the input.
    - Press 'Backspace' to delete the character before the cursor.
    - Press 'Ctrl+C' to cancel the operation.

    Args:
        message (str): The message to display to the user.
        placeholder (str, optional): The placeholder text to display when the input is empty.
        initial_value (str, optional): The initial value of the input.
        validate (Callable[[str], Optional[str]], optional): A function to validate the input.
        default_value (str, optional): The default value to be returned as the value in the raised `CancelException`.
        cancellation_message (str): The message to display if the user cancels the operation.

    Returns:
        str: The user's input.

    Raises:
        CancelException: If the user cancels the operation.
    '''
    
    prompt: Ask = Ask(message, cancellation_message, placeholder, initial_value, default_value, validate)
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
            default_value: Optional[str] = None,
            validate: Optional[Callable[[str], Optional[str]]] = None):
        '''
        Initialize an Ask prompt with the given message, placeholder, initial value, and validation function.

        Args:
            message (str): The message to display to the user.
            cancellation_message (str): The message to display if the user cancels the operation.
            placeholder (str, optional): The placeholder text to display when the input is empty.
            initial_value (str, optional): The initial value of the input.
            default_value (str, optional): The default value to be returned as the value in the raised `CancelException`.
            validate (Callable[[str], Optional[str]], optional): A function to validate the input.

        Raises:
            CancelException: If the user cancels the operation.
        '''

        super().__init__()

        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.placeholder: Optional[str] = placeholder
        self.initial_value: Optional[str] = initial_value
        self.default_value: Optional[str] = default_value
        self.validate: Optional[Callable[[str], Optional[str]]] = validate

        self.render_frame: RenderFrame = RenderFrame()
        self.text_box_controller: TextBoxController = TextBoxController()
        if initial_value: 
            self.text_box_controller.set_input(initial_value, 0)
            self.text_box_controller.cursor_end()
        
        self.propogate_key_after_error = True
        self.allowed_inputs: tuple[str, ...] = self._construct_allowed_inputs()

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str, ...]:
        '''
        Construct a tuple of allowed inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        allowed_chars: tuple[str, ...] = tuple(chr(i) for i in range(32, 127))
        return ('BACKSPACE', 'ENTER', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'TAB', 'SPACE') + allowed_chars

    @override
    def handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        if key not in self.allowed_inputs: key = ''

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

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
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_message_header(
            self.message, 
            theme.text, 
            f'{step_marker_active}  ', 
            theme.active, 
            prefix_active)
        frame_builder.add_lines(*message_lines)
 
        if self.placeholder and len(input_buffer) <= 0:
            placeholder_text: Text = Text(self.placeholder, theme.muted)
            placeholder_text = apply_cursor_style(placeholder_text, 0, theme.cursor)
            frame_builder.add_lines(*build_wrapped_lines(placeholder_text, prefix_active))
        else:
            input_buffer_text: Text = Text(input_buffer, theme.text)
            input_buffer_text = apply_cursor_style(input_buffer_text, input_index, theme.cursor)
            frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_active))
 
        frame_builder.add_line(Text(connector_bar_end, theme.active))
 
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*message_lines)
        
        input_buffer_text: Text = Text(input_buffer, theme.muted)
        frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_muted))
        
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
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        prefix_error: Text = Text(f'{connector_bar_vertical}  ', theme.error)
        closing_prefix_error: Text = Text(f'{connector_bar_end}  ', theme.error)

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_error}  ',
            theme.error,
            prefix_error)
        frame_builder.add_lines(*message_lines)
        
        if self.placeholder and len(input_buffer) <= 0:
            placeholder_text: Text = Text(self.placeholder, theme.muted)
            placeholder_text = apply_cursor_style(placeholder_text, 0, theme.cursor)
            frame_builder.add_lines(*build_wrapped_lines(placeholder_text, prefix_error))
        else:
            input_buffer_text: Text = Text(input_buffer, theme.text)
            input_buffer_text = apply_cursor_style(input_buffer_text, input_index, theme.cursor)
            frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_error))

        validation_error_message: str = self.validate(input_buffer) # self.validate must be defined if we are in the error state, and it must return something
        error_lines: list[Text] = build_message_close(
            validation_error_message,
            theme.error,
            prefix_error,
            closing_prefix_error)
        frame_builder.add_lines(*error_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        if key == 'ENTER' or key is None: return False
        else: return True

    @override
    def handle_cancel(self) -> None:
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

        # Create and render next frame based on the current input buffer and state
        input_buffer: str = self.text_box_controller.get_input()

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        if len(input_buffer) > 0:
            input_buffer_text: Text = Text(input_buffer, text_style)
            frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_muted))
            
        frame_builder.add_line(prefix_muted)
        cancel_lines: list[Text] = build_message_close(
            self.cancellation_message,
            theme.cancel,
            prefix_muted,
            closing_prefix_muted)
        frame_builder.add_lines(*cancel_lines)
        
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, input_buffer if not self.default_value else self.default_value)