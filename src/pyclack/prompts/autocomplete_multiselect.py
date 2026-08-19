from .util import TextBoxController, build_wrapped_lines, build_message_header, build_message_close, apply_cursor_style
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException, ClackOption
from ..terminal import CursorController as cc
from ..config import get_active_theme
from typing import override, Callable
from ..terminal import Stdout
from copy import copy

def autocomplete_multiselect(
    message: str,
    options: list[ClackOption], 
    placeholder: str = 'Type to search...',
    show_instructions: bool = True,
    max_items: int = 7,
    cancellation_message: str = 'Operation Cancelled',
    show_cancellation_message: bool = True,
    filter: Callable[[str, list[ClackOption]], list[ClackOption]] | None = None,
    abort_time: float | None = None) -> list[ClackOption]:
    '''
    Ask the user to select one or more options from a list of options, with autocomplete functionality.
    
    Controls are as follows:
    - Up/Down arrows to navigate the list of options
    - Backspace to delete the last character in the search input
    - Type to filter the list of options
    - Space to select/deselect the currently highlighted option
    - Enter to submit the selected options
    - Press 'Ctrl+C' or 'esc' to cancel the operation
    
    Args:
        message (str): The message to display to the user.
        options (list[ClackOption]): The list of options to display.
        placeholder (str, optional): The placeholder text to display in the search input. Defaults to 'Type to search...'.
        show_instructions (bool, optional): If True, shows the instructions for the prompt. Defaults to True.
        max_items (int, optional): The maximum number of items to display in the list. Defaults to 7.
        cancellation_message (str, optional): The message to display if the user cancels the operation. Defaults to 'Operation Cancelled'.
        show_cancellation_message (bool, optional): If True shows cancellation message, shows no cancellation message if False. Defaults to True.
        filter (Callable[[str, list[ClackOption]], list[ClackOption]] | None, optional): A callable that takes the current search string and the list of options, and returns a filtered list of options. If None, the default filtering behavior is used. Defaults to None.
        abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

    Returns:
        list[ClackOption]: The options selected by the user.

    Raises:
        RuntimeError: If the options list is empty or if all options are disabled.
        CancelException[list[ClackOption]]: If the user cancels the operation.
    '''

    prompt: AutocompleteMultiselect = AutocompleteMultiselect(message, placeholder, cancellation_message, options, show_instructions, max_items, show_cancellation_message, filter, abort_time)
    return prompt.selected_options

class AutocompleteMultiselect(PromptBase):
    '''
    A prompt that allows the user to select one or more options from a list of options, with autocomplete functionality.
    '''

    def __init__(self, 
        message: str,
        placeholder: str,
        cancellation_message: str,
        options: list[ClackOption], 
        show_instructions: bool, 
        max_items: int,
        show_cancellation_message: bool,
        filter: Callable[[str, list[ClackOption]], list[ClackOption]] | None,
        abort_time: float | None):
        '''
        Initialize the Autocomplete Multiselect prompt.

        Args:
            message (str): The message to display to the user.
            placeholder (str): The placeholder text to display in the search input.
            cancellation_message (str): The message to display if the user cancels the operation.
            options (list[ClackOption]): The list of options to display.
            show_instructions (bool): If True, shows the instructions for the prompt.
            max_items (int): The maximum number of items to display in the list.
            show_cancellation_message (bool): If True shows cancellation message, shows no cancellation message if False.
            filter (Callable[[str, list[ClackOption]], list[ClackOption]] | None): A callable that takes the current search string and the list of options, and returns a filtered list of options. If None, the default filtering behavior is used. Defaults to None.
            abort_time (float | None): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel.

        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException: If the user cancels the operation.
        '''

        super().__init__()
            
        self.message: str = message
        self.placeholder: str = placeholder
        self.cancellation_message: str = cancellation_message
        self.options: list[ClackOption] = options
        self.show_instructions: bool = show_instructions
        self.max_items: int = max(5, max_items)
        self.show_cancellation_message: bool = show_cancellation_message
        self.filter: Callable[[str, list[ClackOption]], list[ClackOption]] | None = filter

        self.render_frame: RenderFrame = RenderFrame()
        self.text_inputs: tuple[str, ...] = self._construct_text_inputs()
        self.view_start_index: int = 0
        self.view_window: list[int] = []
        self.view_has_top_ellipsis: bool = False
        self.view_has_bottom_ellipsis: bool = False
        self.show_cursor: bool = False
        self.searched_options: list[ClackOption] = copy(self.options)
        self.text_box_controller: TextBoxController = TextBoxController()
        self.selected_options: list[ClackOption] = []

        if not self.options:
            raise RuntimeError('Options cannot be empty')

        if self._all_options_disabled():
            raise RuntimeError('At least one option must be enabled')
            
        self.active_option_index: int = 0
        if self.searched_options[self.active_option_index].disabled:
            self._move_selection_down()
        
        self._update_view_window()

        self.propogate_key_after_error = True
        self.abort_time = abort_time
        
        self.activate()

    def _update_view_window(self) -> None:
        '''
        Recompute the visible window from scratch, given the current
        selection. Declarative rather than incremental: every call derives
        the unique correct window directly from (active_option_index,
        total, max_items, and the previous view_start_index as a
        minimal-movement hint).
    
        `view_window` contains only indexes into self.searched_options.
        The ellipsis flags indicate whether an ellipsis should be
        rendered above and/or below the visible options.
        '''
    
        total: int = len(self.searched_options)
    
        if total <= self.max_items:
            self.view_start_index = 0
            self.view_window = list(range(total))
            self.view_has_top_ellipsis = False
            self.view_has_bottom_ellipsis = False
            return
    
        capacity: int = self.max_items
        start: int = self.view_start_index
    
        for _ in range(4):
            if self.active_option_index < start:
                start = self.active_option_index
            elif self.active_option_index > start + capacity - 1:
                start = self.active_option_index - capacity + 1
    
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

    def _construct_text_inputs(self) -> tuple[str, ...]:
        '''
        Construct a tuple of text inputs for the prompt.

        Returns:
            tuple[str]: A tuple of text input keys.
        '''

        allowed_chars: tuple[str, ...] = tuple(chr(i) for i in range(32, 127))
        return ('SPACE',) + allowed_chars

    def _all_options_disabled(self) -> bool:
        '''
        Check if all options are disabled.

        Returns:
            bool: True if all options are disabled, False otherwise.
        '''

        return all(option.disabled for option in self.searched_options)

    def _increment_wrap(self) -> None:
        '''
        Increment the selected option index, wrapping around to the end if necessary.
        '''

        new_index: int = self.active_option_index - 1
        if new_index < 0: new_index = len(self.searched_options) - 1
        self.active_option_index = new_index

    def _decrement_wrap(self) -> None:
        '''
        Decrement the selected option index, wrapping around to the beginning if necessary.
        '''

        new_index: int = self.active_option_index + 1
        if new_index >= len(self.searched_options): new_index = 0
        self.active_option_index = new_index

    def _move_selection_up(self) -> None:
        '''
        Move the selection up to the next enabled option, wrapping around if necessary.
        '''

        self._increment_wrap()
        total: int = 0
        while self.searched_options[self.active_option_index].disabled:
            self._increment_wrap()
            total += 1
            if total >= len(self.searched_options) - 1: break

    def _move_selection_down(self) -> None:
        '''
        Move the selection down to the next enabled option, wrapping around if necessary.
        '''

        self._decrement_wrap()
        total: int = 0
        while self.searched_options[self.active_option_index].disabled:
            self._decrement_wrap()
            total += 1
            if total >= len(self.searched_options) - 1: break

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
        if active or selected or option.disabled: option_text += Text(f' ({option.hint})', theme.muted)
        return option_text

    def _update_search(self) -> None:
        '''
        Update the list of searched options based on the current input in the text box controller. 
        Resets the active option index to 0 and updates the view window accordingly.
        '''

        search: str = self.text_box_controller.get_input().lower().strip()
        if not search:
            self.searched_options = copy(self.options)
            self.active_option_index = 0
            return

        def _default_search(search: str, options: list[ClackOption]) -> list[ClackOption]:
            results: list[ClackOption] = [result for result in options if search in result.label.lower().strip()]
            results = sorted(results, key=lambda r: r.label.lower().strip().index(search))
            return results

        self.searched_options = _default_search(search, self.options) if not self.filter else self.filter(search, self.options)
        self.active_option_index = 0
        if self.searched_options and self.searched_options[self.active_option_index].disabled:
            self._move_selection_down()

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        search: str = self.text_box_controller.get_input()

        match key:
            case 'ENTER': return True # Advance to the next state (submit)
            case 'SPACE':
                if self.searched_options and not self.searched_options[self.active_option_index].disabled:
                    current_active_option: ClackOption = self.searched_options[self.active_option_index]
                    if current_active_option in self.selected_options: self.selected_options.remove(current_active_option)
                    else: self.selected_options.append(current_active_option)
            case 'UP': 
                if self.searched_options:
                    self._move_selection_up()
                    self._update_view_window()
                    self.show_cursor = False
            case 'DOWN': 
                if self.searched_options:
                    self._move_selection_down()
                    self._update_view_window()
                    self.show_cursor = False
            case 'LEFT':
                self.text_box_controller.cursor_left()
                self.show_cursor = True
            case 'RIGHT':
                self.text_box_controller.cursor_right()
                self.show_cursor = True
            case 'BACKSPACE':
                self.text_box_controller.delete()
                self._update_search()
                self._update_view_window()
                self.show_cursor = True
            case _:
                map: dict[str, str] = {'SPACE': ' '}

                if key not in self.text_inputs: key = ''
                else: key = map.get(key, key)

                self.text_box_controller.insert(key)
                self._update_search()
                self._update_view_window()
                self.show_cursor = True

        # Create and render next frame based on the current input buffer and state
        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        search = self.text_box_controller.get_input()

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_active}  ',
            theme.active,
            prefix_active)
        frame_builder.add_lines(*message_lines)

        frame_builder.add_line(prefix_active)

        search_text_parts: list[tuple[str, Style] | Text | str] = []
        search_text_parts.append(('Search: ', theme.muted))
        if not search:
            self.show_cursor = False
            search_text_parts.append((self.placeholder, theme.muted))
        else:
            search_input_text: Text = Text(search, theme.muted)
            search_input_text = apply_cursor_style(
                search_input_text,
                self.text_box_controller.get_cursor_position(),
                theme.cursor)
            search_text_parts.append(search_input_text)
            search_text_parts.append((f' ({len(self.searched_options)} matches)'))
        search_text: Text = Text.assemble(*search_text_parts)
        search_lines: list[Text] = build_wrapped_lines(
            search_text,
            prefix_active)
        frame_builder.add_lines(*search_lines)

        if self.view_has_top_ellipsis:
            frame_builder.add_line(prefix_active + Text('...', theme.muted))

        if self.view_window:
            for index in self.view_window:
                option_text: Text = self._build_option_line(
                    self.searched_options[index],
                    True if self.searched_options[index] in self.selected_options else False,
                    True if self.active_option_index == index else False)
                option_text_lines: list[Text] = build_wrapped_lines(
                    option_text,
                    prefix_active)
                frame_builder.add_lines(*option_text_lines)
        else:
            no_matches_text: Text = prefix_active + Text('No matches found', theme.error)
            frame_builder.add_line(no_matches_text)

        if self.view_has_bottom_ellipsis:
            frame_builder.add_line(prefix_active + Text('...', theme.muted))

        if self.show_instructions:
            instructions_text: Text = Text.assemble(
                ('↑/↓ ', theme.muted),
                ('to navigate • ', theme.text),
                ('Enter: ', theme.muted),
                ('confirm • ', theme.text),
                ('Type:', theme.muted),
                (' to search', theme.text))
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
        if not self.selected_options: return False
        
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

        options_text: Text = prefix_muted + Text(f'{len(self.selected_options)} items selected', theme.muted)
        frame_builder.add_line(options_text)

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
        
        search = self.text_box_controller.get_input()

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_error}  ',
            theme.error,
            prefix_error)
        frame_builder.add_lines(*message_lines)

        frame_builder.add_line(prefix_error)

        search_text_parts: list[tuple[str, Style] | Text | str] = []
        search_text_parts.append(('Search: ', theme.muted))
        if not search:
            self.show_cursor = False
            search_text_parts.append((self.placeholder, theme.muted))
        else:
            search_input_text: Text = Text(search, theme.muted)
            search_input_text = apply_cursor_style(
                search_input_text,
                self.text_box_controller.get_cursor_position(),
                theme.cursor)
            search_text_parts.append(search_input_text)
            search_text_parts.append((f' ({len(self.searched_options)} matches)'))
        search_text: Text = Text.assemble(*search_text_parts)
        search_lines: list[Text] = build_wrapped_lines(
            search_text,
            prefix_error)
        frame_builder.add_lines(*search_lines)

        if self.view_has_top_ellipsis:
            frame_builder.add_line(prefix_error + Text('...', theme.muted))

        if self.view_window:
            for index in self.view_window:
                option_text: Text = self._build_option_line(
                    self.searched_options[index],
                    True if self.searched_options[index] in self.selected_options else False,
                    True if self.active_option_index == index else False)
                option_text_lines: list[Text] = build_wrapped_lines(
                    option_text,
                    prefix_error)
                frame_builder.add_lines(*option_text_lines)
        else:
            no_matches_text: Text = prefix_error + Text('No matches found', theme.error)
            frame_builder.add_line(no_matches_text)

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
        raise CancelException[list[ClackOption]](self.cancellation_message, self.selected_options if self.selected_options else list())