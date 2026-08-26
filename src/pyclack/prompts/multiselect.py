from .util import build_wrapped_lines, build_message_header, build_message_close
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException, ClackOption
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override
from copy import copy

def multiselect(
    message: str,
    options: list[ClackOption], 
    show_instructions: bool = True,
    max_items: int = 7,
    abort_time: float | None = None) -> list[ClackOption]:
    '''
    Ask the user to select multiple options from a list of options.

    Controls are as follows:
    - Up/Down arrows or k/j to navigate the options.
    - Space to select/deselect an option.
    - Enter to submit the selected options.
    - Press 'Ctrl+C' or 'esc' to cancel the operation.

    Args:
        message (str): The message to display to the user.
        options (list[ClackOption]): The list of options to display to the user.
        show_instructions (bool, optional): Whether to show instructions for the user. Defaults to True.
        max_items (int, optional): The maximum number of items to display at once. Defaults to 7.
        abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

    Returns:
        list[ClackOption]: The list of selected options.

    Raises:
        RuntimeError: If the options list is empty or if all options are disabled.
        CancelException: If the user cancels the operation.
    '''

    prompt: Multiselect = Multiselect(message, options, show_instructions, max_items, abort_time)
    selected_options: list[ClackOption] = [prompt.options[index] for index in prompt.selected_options]
    return selected_options

class Multiselect(PromptBase):
    '''
    A prompt that allows the user to select multiple options from a list of options.
    '''

    def __init__(self, 
        message: str,
        options: list[ClackOption], 
        show_instructions: bool, 
        max_items: int,
        abort_time: float | None):
        '''
        Initialize a Multiselect prompt.

        Args:
            message (str): The message to display to the user.
            options (list[ClackOption]): The list of options to display to the user.
            show_instructions (bool): Whether to show instructions for the user.
            max_items (int): The maximum number of items to display at once.
            abort_time (float | None): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel.

        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException: If the user cancels the operation.
        '''

        super().__init__()
            
        self.message: str = message
        self.options: list[ClackOption] = options
        self.show_instructions: bool = show_instructions
        self.max_items: int = max(5, max_items)

        if not self.options:
            raise RuntimeError('Options cannot be empty')

        if self._all_options_disabled():
            raise RuntimeError('At least one option must be enabled')
            
        self.focused_option_index: int = 0
        if self.options[self.focused_option_index].disabled:
            self._move_selection_down()

        self.render_frame: RenderFrame = RenderFrame()
        self.control_inputs: tuple[str, ...] = self._construct_control_inputs()
        self.view_start_index: int = 0
        self.view_window: list[int] = []
        self.view_has_top_ellipsis: bool = False
        self.view_has_bottom_ellipsis: bool = False
        self.selected_options: list[int] = []
        
        self._update_view_window()

        self.propagate_key_after_error = True
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
            if self.focused_option_index < start:
                start = self.focused_option_index
            elif self.focused_option_index > start + capacity - 1:
                start = self.focused_option_index - capacity + 1
    
            start = max(0, min(start, total - capacity))
    
            top_ellipsis: bool = start > 0
            bottom_ellipsis: bool = (start + capacity) < total
            new_capacity: int = max(1, self.max_items - int(top_ellipsis) - int(bottom_ellipsis))
    
            if new_capacity == capacity: break
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
        '''
        Check if all options are disabled.

        Returns:
            bool: True if all options are disabled, False otherwise.
        '''

        return all(option.disabled for option in self.options)

    def _increment_wrap(self) -> None:
        '''
        Increment the focused option index, wrapping around to the end if necessary.
        '''

        new_index: int = self.focused_option_index - 1
        if new_index < 0: new_index = len(self.options) - 1
        self.focused_option_index = new_index

    def _decrement_wrap(self) -> None:
        '''
        Decrement the focused option index, wrapping around to the beginning if necessary.
        '''

        new_index: int = self.focused_option_index + 1
        if new_index >= len(self.options): new_index = 0
        self.focused_option_index = new_index

    def _move_selection_up(self) -> None:
        '''
        Move the selection up to the previous enabled option, wrapping around if necessary.
        '''
        
        self._increment_wrap()
        while self.options[self.focused_option_index].disabled:
            self._increment_wrap()

    def _move_selection_down(self) -> None:
        '''
        Move the selection down to the next enabled option, wrapping around if necessary.
        '''

        self._decrement_wrap()
        while self.options[self.focused_option_index].disabled:
            self._decrement_wrap()

    def _build_selected_options_line(self, strikethrough: bool = False) -> Text:
        '''
        Build a line of text representing the selected options.

        Args:
            strikethrough (bool, optional): If True, the text will be strikethrough. Defaults to False.

        Returns:
            Text: A Text object representing the selected options.
        '''

        theme: Theme = get_active_theme()

        selected_options_text: Text = Text('')

        text_style: Style = copy(theme.muted)
        if strikethrough: text_style.strikethrough = True

        selected_options: list[ClackOption] = [self.options[index] for index in self.selected_options]
        for i, selected_option in enumerate(selected_options):
            option_text: Text = Text(selected_option.label, text_style)
            if i != len(selected_options) - 1:
                option_text += Text(', ', theme.muted)
            selected_options_text += option_text

        return selected_options_text

    def _build_option_line(self, option: ClackOption, selected: bool, active: bool) -> Text:
        '''
        Build a line of text representing an option.

        Args:
            option (ClackOption): The option to build the line for.
            selected (bool): Whether the option is selected.
            active (bool): Whether the option is active.

        Returns:
            Text: A Text object representing the option.
        '''

        theme: Theme = get_active_theme()
        selection_widget_checkbox_active: str = theme.symbols.selection_widget_checkbox_active.resolve()
        selection_widget_checkbox_inactive: str = theme.symbols.selection_widget_checkbox_inactive.resolve()
        selection_widget_checkbox_selected: str = theme.symbols.selection_widget_checkbox_selected.resolve()

        disabled_style: Style = copy(theme.muted)
        disabled_style.strikethrough = True
        disabled_style.dim = True

        widget: str = selection_widget_checkbox_inactive if (not active or option.disabled) else selection_widget_checkbox_active
        if selected: widget = selection_widget_checkbox_selected

        widget_style = theme.submit if (selected or active) else theme.muted
        if option.disabled:
            widget_style = copy(theme.muted)
            widget_style.dim = True

        if option.disabled: label_style: Style = disabled_style
        elif not active: label_style = theme.muted
        else: label_style = theme.text

        option_text: Text = Text(widget, widget_style) + ' ' + Text(option.label, label_style)
        if (active or selected or option.disabled) and option.hint: option_text += Text(f' ({option.hint})', theme.muted)
        return option_text

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())

        match key:
            case 'ENTER': return True # Advance to the next state (submit)
            case 'UP' | 'LEFT' | 'k' | 'K' | 'h' | 'H': 
                self._move_selection_up()
                self._update_view_window()
            case 'DOWN' | 'RIGHT' | 'l' | 'L' | 'j' | 'J': 
                self._move_selection_down()
                self._update_view_window()
            case 'SPACE':
                if self.focused_option_index in self.selected_options:
                    self.selected_options.remove(self.focused_option_index)
                else: self.selected_options.append(self.focused_option_index)
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
                True if index in self.selected_options else False,
                True if self.focused_option_index == index else False)
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

        return False

    @override
    def handle_submit(self) -> bool:
        if not self.selected_options: return False # Nothing selected go to next state (error)
        
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

        selected_options_text: Text = self._build_selected_options_line()
        selected_options_lines: list[Text] = build_wrapped_lines(
            selected_options_text,
            prefix_muted)
        frame_builder.add_lines(*selected_options_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True

    @override
    def handle_error(self, key: str | None) -> bool:
        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        prefix_error: Text = Text(f'{connector_bar_vertical}  ', theme.error)
        closing_prefix_error: Text = Text(f'{connector_bar_end}  ', theme.error)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_error}  ',
            theme.error,
            prefix_error)
        frame_builder.add_lines(*message_lines)

        if self.view_has_top_ellipsis:
            frame_builder.add_line(prefix_error + Text('...', theme.muted))

        for index in self.view_window:
            option_text: Text = self._build_option_line(
                self.options[index],
                True if index in self.selected_options else False,
                True if self.focused_option_index == index else False)
            option_text_lines: list[Text] = build_wrapped_lines(
                option_text,
                prefix_error)
            frame_builder.add_lines(*option_text_lines)

        if self.view_has_bottom_ellipsis:
            frame_builder.add_line(prefix_error + Text('...', theme.muted))

        if self.show_instructions:
            instructions_text: Text = Text('↑/↓ ', theme.muted) + Text('to navigate • ', theme.text) + Text('Enter: ', theme.muted) + Text('confirm', theme.text)
            instructions_text_lines: list[Text] = build_wrapped_lines(
                instructions_text,
                prefix_error)
            frame_builder.add_lines(*instructions_text_lines)

        error_lines: list[Text] = build_message_close(
            'Please select at least one option.',
            theme.error,
            prefix_error,
            closing_prefix_error)
        frame_builder.add_lines(*error_lines)

        highlight_style: Style = copy(theme.text)
        highlight_style.bg_color = theme.muted.fg_color
        error_instructions_text: Text = Text.assemble(
            ('Press ', theme.text),
            (' space ', highlight_style),
            (' to select, ', theme.text),
            (' enter ', highlight_style),
            (' to submit', theme.text))
        error_instructions_text_lines: list[Text] = build_wrapped_lines(
            error_instructions_text,
            Text(' ' * len(closing_prefix_error)))
        frame_builder.add_lines(*error_instructions_text_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        if key == 'ENTER' or key is None: return False
        else: return True

    @override
    def handle_cancel(self) -> None:
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        if self.selected_options:
            selected_options_text: Text = self._build_selected_options_line(strikethrough=True)
            selected_options_lines: list[Text] = build_wrapped_lines(
                selected_options_text,
                prefix_muted)
            frame_builder.add_lines(*selected_options_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        selected_options: list[ClackOption] = [self.options[index] for index in self.selected_options]
        raise CancelException[list[ClackOption]](selected_options)