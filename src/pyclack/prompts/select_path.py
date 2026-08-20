from .util import TextBoxController, build_wrapped_lines, build_message_header, build_message_close, apply_cursor_style
from ..renderer import RenderFrame, Text, FrameBuilder, Style, Theme
from .prompt_base import PromptBase, CancelException, ClackOption
from ..terminal import CursorController as cc
from strsimpy.jaro_winkler import JaroWinkler
from ..config import get_active_theme
from typing import override, Callable
from ..terminal import Stdout
from pathlib import Path
from copy import copy
import os

def select_path(
    message: str,
    placeholder: str = 'Type to search...',
    show_instructions: bool = True,
    max_items: int = 7,
    root: Path = Path(os.getcwd()),
    directory: bool = False,
    abort_time: float | None = None) -> Path:
    '''
    Ask the user to select an option from a list of options, with autocomplete functionality.
    
    Controls are as follows:
    - Up/Down arrows to navigate the list of options
    - Backspace to delete the last character in the search input
    - Type to filter the list of options
    - Enter to select the currently highlighted option
    - Press 'Ctrl+C' or 'esc' to cancel the operation
    
    Args:
        message (str): The message to display to the user.
        placeholder (str, optional): The placeholder text to display in the search input. Defaults to 'Type to search...'.
        show_instructions (bool, optional): If True, shows the instructions for the prompt. Defaults to True.
        max_items (int, optional): The maximum number of items to display in the list. Defaults to 7.
        root (Path, optional): The root directory to start the search from. Defaults to the current working directory.
        directory (bool, optional): If True, only directories will be shown in the list of options. If False, both files and directories will be shown. Defaults to False.
        abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
        
    Returns:
         Path: The selected path.
         
    Raises:
        FileNotFoundError: If the root path does not exist.
        CancelException: If the user cancels the operation.
    '''

    prompt: SelectPath = SelectPath(message, root, directory, placeholder, show_instructions, max_items, abort_time)
    return prompt.searched_options[prompt.selected_option_index].value

class SelectPath(PromptBase):
    '''
    A prompt that allows the user to select an option from a list of options, with autocomplete functionality.
    '''

    def __init__(self, 
        message: str,
        root: Path,
        directory: bool,
        placeholder: str,
        show_instructions: bool, 
        max_items: int,
        abort_time: float | None):
        '''
        Initialize the Autocomplete prompt.

        Args:
            message (str): The message to display to the user.
            root (Path): The root directory to start the search from.
            directory (bool): If True, only directories will be shown in the list of options.
            placeholder (str): The placeholder text to display in the search input.
            show_instructions (bool): If True, shows the instructions for the prompt.
            max_items (int): The maximum number of items to display in the list.
            abort_time (float | None): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel.
        '''

        super().__init__()
            
        self.message: str = message
        self.root: Path = root
        self.directory: bool = directory
        self.placeholder: str = placeholder
        self.show_instructions: bool = show_instructions
        self.max_items: int = max(5, max_items)

        if not root.exists():
            raise FileNotFoundError(f'root path "{root}" does not exist')

        self.render_frame: RenderFrame = RenderFrame()
        self.text_inputs: tuple[str, ...] = self._construct_text_inputs()
        self.view_start_index: int = 0
        self.view_window: list[int] = []
        self.view_has_top_ellipsis: bool = False
        self.view_has_bottom_ellipsis: bool = False
        self.show_cursor: bool = False
        self.searched_options: list[ClackOption[Path]] = self._convert_paths_to_options(self._get_directory_contents(self.root))
        self.text_box_controller: TextBoxController = TextBoxController()
        self.jarowinkler: JaroWinkler = JaroWinkler()
            
        self.selected_option_index: int = 0
        self.text_box_controller.set_input(str(self.root), 0)
        self.text_box_controller.cursor_end()
        self._update_view_window()

        self.abort_time = abort_time
        
        self.activate()

    def _convert_paths_to_options(self, paths: list[Path]) -> list[ClackOption[Path]]:
        '''
        Convert a list of Path objects to a list of ClackOption objects.

        Args:
            paths (list[Path]): A list of Path objects.

        Returns:
            list[ClackOption[Path]]: A list of ClackOption objects.
        '''
        
        options: list[ClackOption[Path]] = []
        for path in paths:
            if path.is_file(): options.append(ClackOption(value=path, label=str(path), hint='file'))
            else: options.append(ClackOption(value=path, label=str(path)))
        return options

    def _get_directory_contents(self, directory: Path) -> list[Path]:
        '''
        Get the contents of a directory as a list of Path objects. If the directory does not exist, 
        return an empty list. If the directory is a file, return the contents of its parent directory.

        Args:
            directory (Path): The directory to get the contents of.

        Returns:
            list[Path]: A list of Path objects representing the contents of the directory.
        '''
        
        directory = directory.absolute()
        
        if directory.is_dir():
            try:
                dir_contents: list[Path] = list(directory.iterdir())
                return dir_contents
            except PermissionError: return []
        else:
            dir_parent: Path = directory.parent
            if not dir_parent.exists(): return []
            try:
                dir_contents = list(dir_parent.iterdir())
            except PermissionError: dir_contents = []
            return dir_contents

    def _update_view_window(self) -> None:
        '''
        Recompute the visible window from scratch, given the current
        selection. Declarative rather than incremental: every call derives
        the unique correct window directly from (selected_option_index,
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
            if self.selected_option_index < start:
                start = self.selected_option_index
            elif self.selected_option_index > start + capacity - 1:
                start = self.selected_option_index - capacity + 1
    
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

    def _increment_wrap(self) -> None:
        '''
        Increment the selected option index, wrapping around to the end if necessary.
        '''

        new_index: int = self.selected_option_index - 1
        if new_index < 0: new_index = len(self.searched_options) - 1
        self.selected_option_index = new_index

    def _decrement_wrap(self) -> None:
        '''
        Decrement the selected option index, wrapping around to the beginning if necessary.
        '''

        new_index: int = self.selected_option_index + 1
        if new_index >= len(self.searched_options): new_index = 0
        self.selected_option_index = new_index

    def _move_selection_up(self) -> None:
        '''
        Move the selection up to the next enabled option, wrapping around if necessary.
        '''

        self._increment_wrap()
        total: int = 0
        while self.searched_options[self.selected_option_index].disabled:
            self._increment_wrap()
            total += 1
            if total >= len(self.searched_options) - 1: break

    def _move_selection_down(self) -> None:
        '''
        Move the selection down to the next enabled option, wrapping around if necessary.
        '''

        self._decrement_wrap()
        total: int = 0
        while self.searched_options[self.selected_option_index].disabled:
            self._decrement_wrap()
            total += 1
            if total >= len(self.searched_options) - 1: break

    def _build_option_line(self, option: ClackOption, selected: bool) -> Text:
        '''
        Build a line of text for the given option.

        Args:
            option (ClackOption): The option to build the line for.
            selected (bool): Whether the option is currently selected.

        Returns:
            Text: The styled text for the option line.
        '''

        theme: Theme = get_active_theme()
        selection_widget_radio_active: str = theme.symbols.selection_widget_radio_active.resolve()
        selection_widget_radio_inactive: str = theme.symbols.selection_widget_radio_inactive.resolve()

        widget: str = selection_widget_radio_inactive if (not selected or option.disabled) else selection_widget_radio_active
        widget_style = theme.submit if selected else theme.muted

        if not selected: label_style = theme.muted
        else: label_style = theme.text
       
        option_text: Text = Text(widget, widget_style) + ' ' + Text(option.label, label_style)
        if option.hint:
            hint_style: Style = copy(theme.muted)
            hint_style.bold = True
            hint_style.dim = True
            option_text += Text(f' ({option.hint})', hint_style)
        return option_text

    def _update_search(self, search: str) -> None:
        '''
        Update the list of searched options based on the current input in the text box controller. 
        Resets the selected option index to 0 and updates the view window accordingly.

        Args:
            search (str): The current input in the text box controller.
        '''

        if not search: search = str(self.root)

        base_path: Path = Path(search.strip())

        base_option: ClackOption[Path] = ClackOption[Path](value=base_path, label=str(base_path))
        if base_path.is_file(): base_option.hint = 'file'

        current_paths: list[Path] = self._get_directory_contents(base_path)
        options: list[ClackOption[Path]] = self._convert_paths_to_options(current_paths)

        if self.directory: options = [option for option in options if option.value.is_dir()]

        if base_path.exists() and not base_path.is_file() and not options: 
            options.append(base_option)
            
        if self.directory: options = [option for option in options if option.value.is_dir()]

        if base_path.exists():
            self.selected_option_index = 0
            if base_path.is_file():
                file_name: str = base_path.name.strip()
                options = sorted(options, key=lambda r: self.jarowinkler.similarity(file_name, r.value.name.strip()), reverse=True)
            self.searched_options = options
            return

        search_term: str = base_path.name.strip()
        results: list[ClackOption[Path]] = [r for r in options if search_term in r.value.name.strip()]
        results = sorted(results, key=lambda r: r.value.name.strip().index(search_term))
        self.selected_option_index = 0
        self.searched_options = results

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        search: str = self.text_box_controller.get_input()

        match key:
            case 'ENTER': 
                if self.searched_options: 
                    return True # Advance to the next state (submit)
            case 'TAB':
                if self.searched_options:
                    current_option: ClackOption[Path] = self.searched_options[self.selected_option_index]
                    self.text_box_controller.set_input(str(current_option.value), 0)
                    self.text_box_controller.cursor_end()
                    if current_option.value.is_dir():
                        self.text_box_controller.insert('\\')
                    search = self.text_box_controller.get_input()
                    self._update_search(search)
                    self._update_view_window()
                    self.show_cursor = True
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
                search = self.text_box_controller.get_input()
                self._update_search(search)
                self._update_view_window()
                self.show_cursor = True
            case _:
                map: dict[str, str] = {'SPACE': ' '}

                if key not in self.text_inputs: key = ''
                else: key = map.get(key, key)

                self.text_box_controller.insert(key)
                search = self.text_box_controller.get_input()
                self._update_search(search)
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
                    True if self.selected_option_index == index else False)
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
                (' to search • ', theme.text),
                ('Tab: ', theme.muted),
                ('autocomplete', theme.text))
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
            Text(self.searched_options[self.selected_option_index].label, theme.muted),
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

        if self.searched_options and not self.searched_options[self.selected_option_index].disabled:
            strikethrough_style: Style = copy(theme.muted)
            strikethrough_style.strikethrough = True
            option_lines: list[Text] = build_wrapped_lines(
                Text(self.searched_options[self.selected_option_index].label, strikethrough_style),
                prefix_muted)
            frame_builder.add_lines(*option_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException[Path](self.searched_options[self.selected_option_index].value if self.searched_options else None)