from .util import build_wrapped_lines, build_message_header, build_message_close, apply_cursor_style, TextBoxController
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException, ClackOption
from typing import Any, Optional, override
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from copy import copy

def select(
    message: str,
    options: list[ClackOption], 
    show_instructions: bool = True,
    max_items: int = 7,
    cancellation_message: str = 'Operation Cancelled',
    show_cancellation_message: bool = True,
    abort_time: Optional[float] = None) -> ClackOption:

    prompt: Select = Select(message, cancellation_message, options, show_instructions, max_items, show_cancellation_message, abort_time)
    return prompt.options[prompt.selected_option_index]

class Select(PromptBase):
    def __init__(self, 
        message: str,
        cancellation_message: str,
        options: list[ClackOption], 
        show_instructions: bool, 
        max_items: int,
        show_cancellation_message: bool,
        abort_time: Optional[float]):

        super().__init__()
            
        self.message: str = message
        self.cancellation_message: str = cancellation_message
        self.options: list[ClackOption] = options
        self.show_instructions: bool = show_instructions
        self.max_items: int = max(5, max_items)
        self.show_cancellation_message: bool = show_cancellation_message

        if self._all_options_disabled():
            raise RuntimeError('At least one option must be enabled')
            
        self.selected_option_index: int = 0
        if self.options[self.selected_option_index].disabled:
            self._move_selection_down()

        self.render_frame: RenderFrame = RenderFrame()
        self.control_inputs: tuple[str, ...] = self._construct_control_inputs()
        self.view_start_index: int = 0
        self.view_window: list[int] = []
        self.view_has_top_ellipsis: bool = False
        self.view_has_bottom_ellipsis: bool = False
        
        self._update_view_window()

        self.abort_time = abort_time
        
        self.activate()

    def _update_view_window(self) -> None:
        '''
        Recompute the visible window from scratch, given the current
        selection. Declarative rather than incremental: every call derives
        the unique correct window directly from (selected_option_index,
        total, max_items, and the previous view_start_index as a
        minimal-movement hint).
    
        `view_window` contains only indexes into self.options.
        The ellipsis flags indicate whether an ellipsis should be
        rendered above and/or below the visible options.
        '''
    
        total: int = len(self.options)
    
        if total <= self.max_items:
            self.view_start_index = 0
            self.view_window = list(range(total))
            self.view_has_top_ellipsis = False
            self.view_has_bottom_ellipsis = False
            return
    
        capacity: int = self.max_items
        start: int = self.view_start_index
    
        for _ in range(4):
            if self.selected_option_index < start:
                start = self.selected_option_index
            elif self.selected_option_index > start + capacity - 1:
                start = self.selected_option_index - capacity + 1
    
            start = max(0, min(start, total - capacity))
    
            top_ellipsis: bool = start > 0
            bottom_ellipsis: bool = (start + capacity) < total
            new_capacity: int = max(1, self.max_items - int(top_ellipsis) - int(bottom_ellipsis))
    
            if new_capacity == capacity:
                break
            capacity = new_capacity
    
        start = max(0, min(start, total - capacity))
        self.view_start_index = start
        self.view_window = list(range(start, start + capacity))
        self.view_has_top_ellipsis = start > 0
        self.view_has_bottom_ellipsis = (start + capacity) < total

    def _construct_control_inputs(self) -> tuple[str, ...]:
        '''
        Construct a tuple of control inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        return ('LEFT', 'RIGHT', 'UP', 'DOWN', 'h', 'j', 'k', 'l', 'H', 'J', 'K', 'L')

    def _all_options_disabled(self) -> bool:
        return all(option.disabled for option in self.options)

    def _increment_wrap(self) -> None:
        new_index: int = self.selected_option_index - 1
        if new_index < 0: new_index = len(self.options) - 1
        self.selected_option_index = new_index

    def _decrement_wrap(self) -> None:
        new_index: int = self.selected_option_index + 1
        if new_index >= len(self.options): new_index = 0
        self.selected_option_index = new_index

    def _move_selection_up(self) -> None:
        self._increment_wrap()
        while self.options[self.selected_option_index].disabled:
            self._increment_wrap()

    def _move_selection_down(self) -> None:
        self._decrement_wrap()
        while self.options[self.selected_option_index].disabled:
            self._decrement_wrap()

    def _build_option_line(self, option: ClackOption, selected: bool) -> Text:
        theme: Theme = get_active_theme()
        selection_widget_radio_active: str = theme.symbols.selection_widget_radio_active.resolve()
        selection_widget_radio_inactive: str = theme.symbols.selection_widget_radio_inactive.resolve()

        disabled_style: Style = copy(theme.muted)
        disabled_style.strikethrough = True
        disabled_style.dim = True

        widget: str = selection_widget_radio_inactive if (not selected or option.disabled) else selection_widget_radio_active
        widget_style = theme.submit if selected else theme.muted

        if option.disabled: label_style: Style = disabled_style
        elif not selected: label_style = theme.muted
        else: label_style = theme.text
       
        option_text: Text = Text(widget, widget_style) + ' ' + Text(option.label, label_style)
        if selected or option.disabled: option_text += Text(f' ({option.hint})', theme.muted)
        return option_text

    @override
    def handle_active(self, key: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        match key:
            case 'ENTER': return True # Advance to the next state (submit)
            case 'UP' | 'LEFT' | 'k' | 'K' | 'h' | 'H': 
                self._move_selection_up()
                self._update_view_window()
            case 'DOWN' | 'RIGHT' | 'l' | 'L' | 'j' | 'J': 
                self._move_selection_down()
                self._update_view_window()
            case _: pass

        # Create and render next frame based on the current input buffer and state
        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_active}  ',
            theme.active,
            prefix_active)
        frame_builder.add_lines(*message_lines)

        if self.view_has_top_ellipsis:
            frame_builder.add_line(prefix_active + Text('...', theme.muted))

        for index in self.view_window:
            option_text: Text = self._build_option_line(
                self.options[index],
                True if self.selected_option_index == index else False)
            option_text_lines: list[Text] = build_wrapped_lines(
                option_text,
                prefix_active)
            frame_builder.add_lines(*option_text_lines)

        if self.view_has_bottom_ellipsis:
            frame_builder.add_line(prefix_active + Text('...', theme.muted))

        if self.show_instructions:
            instructions_text: Text = Text('↑/↓ ', theme.muted) + Text('to navigate • ', theme.text) + Text('Enter: ', theme.muted) + Text('confirm', theme.text)
            instructions_text_lines: list[Text] = build_wrapped_lines(
                instructions_text,
                prefix_active)
            frame_builder.add_lines(*instructions_text_lines)

        frame_builder.add_line(Text(f'{connector_bar_end}  ', theme.active))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        option_lines: list[Text] = build_wrapped_lines(
            Text(self.options[self.selected_option_index].label, theme.muted),
            prefix_muted)
        frame_builder.add_lines(*option_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True

    @override
    def handle_cancel(self) -> None:
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        strikethrough_style: Style = copy(theme.muted)
        strikethrough_style.strikethrough = True
        option_lines: list[Text] = build_wrapped_lines(
            Text(self.options[self.selected_option_index].label, strikethrough_style),
            prefix_muted)
        frame_builder.add_lines(*option_lines)
        
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
        raise CancelException[ClackOption](self.cancellation_message, self.options[self.selected_option_index])