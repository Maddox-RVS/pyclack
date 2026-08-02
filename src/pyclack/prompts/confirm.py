from ..renderer import Text, RenderFrame, FrameBuilder, Theme, Style
from ..prompts.util import build_wrapped_input_lines
from ..prompts import PromptBase, CancelException
from ..terminal import CursorController as cc
from typing import override, Optional
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

def confirm(message: str, cancellation_message: str = 'Operation Cancelled', default_option: bool = True) -> bool:
    '''
    Prompt the user for a yes/no confirmation. Controls are as follows:
    - Use the arrow keys (or h/j/k/l) to toggle between 'Yes' and 'No'.
    - Press 'Enter' to submit the selection.

    Args:
        message (str): The message to display to the user.
        cancellation_message (str): The message to display if the user cancels the operation.
        default_option (bool): The default option for the confirmation.

    Returns:
        bool: The user's confirmation.

    Raises:
        CancelException: If the user cancels the operation.
    '''

    prompt: Confirm = Confirm(message, cancellation_message, default_option)
    return prompt.selected_confirmation

class Confirm(PromptBase):
    '''
    A prompt for a yes/no confirmation.
    '''

    def __init__(self, 
                 message: str, 
                 cancellation_message: str,
                 default_option: bool = True):
        '''
        Initialize a Confirm prompt with the given message, cancellation message, and default option.

        Args:
            message (str): The message to display to the user.
            cancellation_message (str): The message to display if the user cancels the operation.
            default_option (bool): The default option for the confirmation.

        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        super().__init__()

        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.selected_confirmation: bool = default_option
        self.render_frame: RenderFrame = RenderFrame()
        self.allowed_inputs: tuple[str] = self._construct_allowed_inputs()

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str]:
        '''
        Construct a tuple of allowed inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        return ('LEFT', 'RIGHT', 'UP', 'DOWN', 'h', 'j', 'k', 'l', 'H', 'J', 'K', 'L')

    @override
    def handle_active(self, key: Optional[str]):
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        selection_widget_radio_active: str = theme.symbols.selection_widget_radio_active.resolve()
        selection_widget_radio_inactive: str = theme.symbols.selection_widget_radio_inactive.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix: str = f'{connector_bar_vertical}  '

        if key == 'ENTER': return True # Advance to the next state (submit)
        elif key in self.allowed_inputs: self.selected_confirmation = not self.selected_confirmation

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.active)
        message_lines[0] = Text(step_marker_active, theme.active) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)

        yes_text_style: Style = theme.text if self.selected_confirmation else theme.muted
        yes_symbol_style: Style = theme.submit if self.selected_confirmation else theme.muted
        yes_symbol: str = selection_widget_radio_active if self.selected_confirmation else selection_widget_radio_inactive
        no_text_style: Style = theme.text if not self.selected_confirmation else theme.muted
        no_symbol_style: Style = theme.submit if not self.selected_confirmation else theme.muted
        no_symbol: str = selection_widget_radio_active if not self.selected_confirmation else selection_widget_radio_inactive

        confirmation_line: Text = Text.assemble(
            (connector_bar_vertical, theme.active), '  ',
            (yes_symbol, yes_symbol_style), ' ',
            ('Yes ', yes_text_style),
            ('/ ', theme.muted),
            (no_symbol, no_symbol_style), ' ',
            ('No', no_text_style))
        frame_builder.add_line(confirmation_line)

        frame_builder.add_line(Text(connector_bar_end, theme.active))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self):
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix: str = f'{connector_bar_vertical}  '

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_submit, theme.submit) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)

        confirmation_text: str = 'Yes' if self.selected_confirmation else 'No'
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted) + '  ' + Text(confirmation_text, theme.muted))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return True

    @override
    def handle_cancel(self):
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix: str = f'{connector_bar_vertical}  '

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_wrapped_input_lines(self.message, prefix, 0, theme.text, theme.muted)
        message_lines[0] = Text(step_marker_cancel, theme.cancel) + '  ' + Text(message_lines[0].get_raw_text()[3:], theme.text)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        confirmation_text: str = 'Yes' if self.selected_confirmation else 'No'
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted) + '  ' + Text(confirmation_text, text_style))
        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        cancel_lines: list[Text] = build_wrapped_input_lines(self.cancellation_message, prefix, 0, theme.cancel, theme.muted)
        last_index: int = len(cancel_lines) - 1
        cancel_lines[last_index] = Text(connector_bar_end, theme.muted) + '  ' + Text(cancel_lines[last_index].get_raw_text()[3:], theme.cancel)
        frame_builder.add_lines(*cancel_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException(self.cancellation_message, self.selected_confirmation)