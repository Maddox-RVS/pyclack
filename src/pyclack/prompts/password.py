from .util import build_wrapped_lines, build_message_header, build_message_close, apply_cursor_style, TextBoxController
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme, Symbol
from .prompt_base import PromptBase, CancelException
from typing import Callable, Optional, override
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

def password(message: str, 
        mask: Optional[Symbol] = None,
        show_nothing: bool = False,
        clear_on_error: bool = False,
        validate: Optional[Callable[[str], Optional[str]]] = None,
        cancellation_message: str = 'Operation Cancelled') -> str:
    '''
    Ask the user for input as a password.
    Controls are as follows:
    - Backspace: Delete the last character in the input buffer.
    - Enter: Submit the input as the password.
    - Ctrl+C: Cancel the operation.

    Args:
        message (str): The message to display to the user.
        mask (Symbol, optional): The symbol to use for masking the input. Defaults to None
        show_nothing (bool, optional): If True, the input will not be displayed at all. Defaults to False.
        clear_on_error (bool, optional): If True, the input buffer will be cleared on error. Defaults to False.
        validate (Callable[[str], Optional[str]], optional): A function to validate the input. Defaults to None.
        cancellation_message (str): The message to display if the user cancels the operation.

    Returns:
        str: The user's input as a password.

    Raises:
        CancelException: If the user cancels the operation.
    '''
    
    prompt: Password = Password(message, cancellation_message, mask, show_nothing, clear_on_error, validate)
    return prompt.text_box_controller.get_input()

class Password(PromptBase):
    def __init__(self,
            message: str,
            cancellation_message: str,
            mask: Optional[Symbol] = None,
            show_nothing: bool = False,
            clear_on_error: bool = False,
            validate: Optional[Callable[[str], Optional[str]]] = None):
        '''
        Initialize a Password prompt with the given message, mask, and validation function.

        Args:
            message (str): The message to display to the user.
            cancellation_message (str): The message to display if the user cancels the operation.
            mask (Symbol, optional): The symbol to use for masking the input. Defaults to None.
            show_nothing (bool, optional): If True, the input will not be displayed at all. Defaults to False.
            clear_on_error (bool, optional): If True, the input buffer will be cleared on error. Defaults to False.
            validate (Callable[[str], Optional[str]], optional): A function to validate the input. Defaults to None.

        Raises:
            CancelException: If the user cancels the operation.
        '''

        super().__init__()

        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.mask: Optional[Symbol] = mask
        self.show_nothing: bool = show_nothing
        self.clear_on_error: bool = clear_on_error
        self.validate: Optional[Callable[[str], Optional[str]]] = validate

        self.render_frame: RenderFrame = RenderFrame()
        self.text_box_controller: TextBoxController = TextBoxController()
        
        self.propogate_key_after_error = True
        self.allowed_inputs: tuple[str] = self._construct_allowed_inputs()

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str, ...]:
        '''
        Construct a tuple of allowed inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        allowed_chars: tuple[str, ...] = tuple(chr(i) for i in range(32, 127))
        return ('BACKSPACE', 'ENTER', 'TAB', 'SPACE') + allowed_chars

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
        else:
            map: dict[str, str] = {
                'SPACE': ' ',
                'TAB': '\t'}  
            char: str = map.get(key, key) # Translate key to character (if applicable)
            if key != '': self.text_box_controller.insert(char)

        # Create and render next frame based on the current input buffer and state
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''
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
        
        input_buffer_text: Text = Text(input_buffer, theme.text)
        if not self.show_nothing: input_buffer_text = apply_cursor_style(input_buffer_text, input_index, theme.cursor)
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
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*message_lines)
        
        input_buffer_text: Text = Text(input_buffer, theme.text)
        frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_muted))
        
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate and self.validate(self.text_box_controller.get_input()) else True

    @override
    def handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        if self.clear_on_error: self.text_box_controller.set_input('', 0)

        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        prefix_error: Text = Text(f'{connector_bar_vertical}  ', theme.error)
        closing_prefix_error: Text = Text(f'{connector_bar_end}  ', theme.error)

        # Create and render next frame based on the current input buffer and state
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''
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
        
        input_buffer_text: Text = Text(input_buffer, theme.text)
        if not self.show_nothing: input_buffer_text = apply_cursor_style(input_buffer_text, input_index, theme.cursor)
        frame_builder.add_lines(*build_wrapped_lines(input_buffer_text, prefix_error))
        
        validation_error_message: str = self.validate(self.text_box_controller.get_input()) # self.validate must be defined if we are in the error state
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
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''

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
            
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))
        
        cancel_lines: list[Text] = build_message_close(
            self.cancellation_message,
            theme.cancel,
            prefix_muted,
            closing_prefix_muted)
        frame_builder.add_lines(*cancel_lines)
        
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, self.text_box_controller.get_input())