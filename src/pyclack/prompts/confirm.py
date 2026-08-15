from ..prompts.util import build_wrapped_lines, build_message_header, build_message_close
from ..renderer import Text, RenderFrame, FrameBuilder, Theme, Style
from ..prompts import PromptBase, CancelException
from ..terminal import CursorController as cc
from typing import override, Optional
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

def confirm(message: str,
            active: str = 'Yes',
            inactive: str = 'No',
            vertical: bool = False,
            cancellation_message: str = 'Operation Cancelled',
            show_cancellation_message: bool = True,
            default_option: bool = True,
            abort_time: Optional[float] = None) -> bool:
    '''
    Prompt the user for a yes/no confirmation. Controls are as follows:
    - Use the arrow keys (or h/j/k/l) to toggle between 'Yes' and 'No'.
    - Press 'Enter' to submit the selection.

    Args:
        message (str): The message to display to the user.
        active (str): The text to display for the active (true) option.
        inactive (str): The text to display for the inactive (false) option.
        cancellation_message (str): The message to display if the user cancels the operation.
        show_cancellation_message (bool, optional): If True shows cancellation message, shows no cancellation message if False. Defaults to True.
        default_option (bool): The default option for the confirmation.
        abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

    Returns:
        bool: The user's confirmation.

    Raises:
        CancelException: If the user cancels the operation.
    '''

    prompt: Confirm = Confirm(message, active, inactive, vertical, cancellation_message, default_option, show_cancellation_message, abort_time)
    return prompt.selected_confirmation

class Confirm(PromptBase):
    '''
    A prompt for a yes/no confirmation.
    '''

    def __init__(self, 
                 message: str,
                 active: str,
                 inactive: str,
                 vertical: bool,
                 cancellation_message: str,
                 default_option: bool = True,
                 show_cancellation_message: bool = True,
                 abort_time: Optional[float] = None):
        '''
        Initialize a Confirm prompt with the given message, cancellation message, and default option.

        Args:
            message (str): The message to display to the user.
            active (str): The text to display for the active (true) option.
            inactive (str): The text to display for the inactive (false) option.
            cancellation_message (str): The message to display if the user cancels the operation.
            default_option (bool): The default option for the confirmation.
            show_cancellation_message (bool, optional): If True shows cancellation message, shows no cancellation message if False. Defaults to True.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        super().__init__()

        self.message: str = message
        self.active: str = active
        self.inactive: str = inactive
        self.vertical: bool = vertical
        self.cancellation_message: str = cancellation_message
        self.show_cancellation_message: bool = show_cancellation_message
        self.selected_confirmation: bool = default_option
        self.render_frame: RenderFrame = RenderFrame()
        self.allowed_inputs: tuple[str, ...] = self._construct_allowed_inputs()

        self.abort_time = abort_time

        super().activate()

    def _construct_allowed_inputs(self) -> tuple[str, ...]:
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
        prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)

        if key == 'ENTER': return True # Advance to the next state (submit)
        elif key in self.allowed_inputs: self.selected_confirmation = not self.selected_confirmation

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_active}  ',
            theme.active,
            prefix_active)
        frame_builder.add_lines(*message_lines)

        yes_text_style: Style = theme.text if self.selected_confirmation else theme.muted
        yes_symbol_style: Style = theme.submit if self.selected_confirmation else theme.muted
        yes_symbol: str = selection_widget_radio_active if self.selected_confirmation else selection_widget_radio_inactive
        no_text_style: Style = theme.text if not self.selected_confirmation else theme.muted
        no_symbol_style: Style = theme.submit if not self.selected_confirmation else theme.muted
        no_symbol: str = selection_widget_radio_active if not self.selected_confirmation else selection_widget_radio_inactive

        if not self.vertical:
            confirmation_line: Text = Text.assemble(
                (yes_symbol, yes_symbol_style), ' ',
                (f'{self.active} ', yes_text_style),
                ('/ ', theme.muted),
                (no_symbol, no_symbol_style), ' ',
                (f'{self.inactive} ', no_text_style))
        else:
            confirmation_line = Text.assemble(
                (yes_symbol, yes_symbol_style), ' ',
                (f'{self.active} ', yes_text_style),
                '\n',
                (no_symbol, no_symbol_style), ' ',
                (f'{self.inactive}', no_text_style))
        confirmation_lines: list[Text] = build_wrapped_lines(confirmation_line, prefix_active)
        frame_builder.add_lines(*confirmation_lines)

        frame_builder.add_line(Text(connector_bar_end, theme.active))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    @override
    def handle_submit(self):
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        confirmation_text: Text = Text(self.active if self.selected_confirmation else self.inactive, theme.muted)
        confirmation_lines: list[Text] = build_wrapped_lines(confirmation_text, prefix_muted)
        frame_builder.add_lines(*confirmation_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        Stdout.put(cc.show_cursor())
        return True

    @override
    def handle_cancel(self):
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(Text(connector_bar_vertical, theme.muted))

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        confirmation_text: Text = Text(self.active if self.selected_confirmation else self.inactive, text_style)
        confirmation_lines: list[Text] = build_wrapped_lines(confirmation_text, prefix_muted)
        frame_builder.add_lines(*confirmation_lines)

        if self.show_cancellation_message:
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
        raise CancelException(self.cancellation_message, str(self.selected_confirmation))