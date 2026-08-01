from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme, Symbol
from .util import build_wrapped_input_lines, TextBoxController
from .prompt_base import PromptBase, CancelException
from typing import Callable, Optional, override
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

def password(message: str, 
        mask: Optional[Symbol] = None,
        show_nothing: bool = False,
        validate: Optional[Callable[[str], Optional[str]]] = None,
        cancellation_message: str = 'Operation Cancelled') -> str:
    '''
    Ask the user for input as a password.

    Args:
        message (str): The message to display to the user.
        mask (Symbol, optional): The symbol to use for masking the input. Defaults to None
        show_nothing (bool, optional): If True, the input will not be displayed at all. Defaults to False.
        validate (Callable[[str], Optional[str]], optional): A function to validate the input. Defaults to None.
        cancellation_message (str): The message to display if the user cancels the operation.

    Returns:
        str: The user's input as a password.

    Raises:
        CancelException: If the user cancels the operation.
    '''
    
    prompt: Password = Password(message, cancellation_message, mask, show_nothing, validate)
    return prompt.text_box_controller.get_input()

class Password(PromptBase):
    def __init__(self,
            message: str,
            cancellation_message: str,
            mask: Optional[Symbol] = None,
            show_nothing: bool = False,
            validate: Optional[Callable[[str], Optional[str]]] = None):
        '''
        Initialize a Password prompt with the given message, mask, and validation function.

        Args:
            message (str): The message to display to the user.
            cancellation_message (str): The message to display if the user cancels the operation.
            mask (Symbol, optional): The symbol to use for masking the input. Defaults to None.
            show_nothing (bool, optional): If True, the input will not be displayed at all. Defaults to False.
            validate (Callable[[str], Optional[str]], optional): A function to validate the input. Defaults to None.

        Raises:
            CancelException: If the user cancels the operation.
        '''

        super().__init__()

        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.mask: Optional[Symbol] = mask
        self.show_nothing: bool = show_nothing
        self.validate: Optional[Callable[[str], Optional[str]]] = validate

        self.render_frame: RenderFrame = RenderFrame()
        self.text_box_controller: TextBoxController = TextBoxController()
        
        self.propogate_key_after_error = True
        self.allowed_inputs: tuple[str] = self._construct_allowed_inputs()

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str]:
        '''
        Construct a tuple of allowed inputs for the prompt.
        '''

        allowed_chars: tuple[str] = tuple(chr(i) for i in range(32, 127))
        return ('BACKSPACE', 'ENTER', 'TAB', 'SPACE') + allowed_chars

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
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.active)
        message_lines[0] = Text(step_marker_active, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.active)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.text, theme.active, not self.show_nothing))
        frame_builder.add_line(Text(connector_bar_end, style=theme.active))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()

        # Create and render next frame based on the current input buffer and state
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] =  build_wrapped_input_lines(self.message, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_submit, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.submit)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.muted, theme.muted))
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return False if self.validate and self.validate(self.text_box_controller.get_input()) else True

    @override
    def handle_error(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()

        # Create and render next frame based on the current input buffer and state
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''
        input_index: int = self.text_box_controller.get_cursor_position()

        frame_builder: FrameBuilder = FrameBuilder()
        message_lines: list[Text] = build_wrapped_input_lines(self.message, 0, theme.text, theme.error)
        message_lines[0] = Text(step_marker_error, Text(message_lines[0].get_raw_text()[1:], style=theme.text), style=theme.error)
        frame_builder.add_lines(*message_lines)
        frame_builder.add_lines(*build_wrapped_input_lines(input_buffer, input_index, theme.text, theme.error, not self.show_nothing))
        validation_error_message: str = self.validate(self.text_box_controller.get_input()) # self.validate must be defined if we are in the error state
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
        mask: str = self.mask.resolve() if self.mask else theme.symbols.selection_widget_password_mask.resolve()
        input_buffer: str = mask * len(self.text_box_controller.get_input()) if not self.show_nothing else ''
        input_index: int = self.text_box_controller.get_cursor_position()

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
        raise CancelException(self.cancellation_message, self.text_box_controller.get_input())