from ..prompts.util import build_message_header, build_message_close, build_wrapped_lines
from ..renderer import Text, Theme, Style, RenderFrame, FrameBuilder
from .prompt_base import PromptBase, CancelException, ClackOption
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override
from copy import copy

def select_key(
    message: str,
    options: list[ClackOption[str]],
    case_sensitive: bool = True,
    abort_time: float | None = None) -> ClackOption[str]:
    '''
    Prompt the user to select an option by pressing a key.

    Controls are as follows:
    - Press the key corresponding to the desired option to select it.
    - Press 'Enter' to select the first option.
    - Press 'Ctrl+C' or 'esc' to cancel the prompt.

    Args:
        message (str): The message to display to the user.
        options (list[ClackOption[str]]): A list of ClackOption objects representing the available options. 
        case_sensitive (bool): Whether the key selection should be case-sensitive.
        abort_time (float | None): The time after which the prompt should be aborted, or None if no timeout is set.

    Returns:
        ClackOption[str]: The selected option.

    Raises:
        RuntimeError: If the options list is empty, all options are disabled, duplicate option values are present, option value is not a valid key, or option value is not of type str.
        CancelException: If the prompt is cancelled by the user.
    '''
        
    prompt: SelectKey = SelectKey(message, options, case_sensitive, abort_time)
    return prompt.selected_option # Must be initialized if prompt submits successfully

class SelectKey(PromptBase):
    '''
    A prompt that allows the user to select an option by pressing a key.
    '''
    
    def __init__(self,
        message: str,
        options: list[ClackOption[str]],
        case_sensitive: bool,
        abort_time: float | None):
        '''
        Initialize a SelectKey prompt.

        Args:
            message (str): The message to display to the user.
            options (list[ClackOption[str]]): A list of ClackOption objects representing the available options.
            case_sensitive (bool): Whether the key selection should be case-sensitive.
            abort_time (float | None): The time after which the prompt should be aborted, or None if no timeout is set.

        Raises:
            RuntimeError: If the options list is empty, all options are disabled, duplicate option values are present, option value is not a valid key, or option value is not of type str.
            CancelException: If the prompt is cancelled by the user.
        '''
            
        super().__init__()

        self.message: str = message
        self.options: list[ClackOption[str]] = options
        self.case_sensitive: bool = case_sensitive

        if not self.options:
            raise RuntimeError('Options cannot be empty')
        if self._all_options_disabled(self.options):
            raise RuntimeError('At least one option must be enabled')

        self.special_allowed_keys: tuple[str, ...] = ('LEFT', 'RIGHT', 'UP', 'DOWN', 'TAB', 'SPACE')
        self.allowed_keys: tuple[str, ...] = self._construct_allowed_keys()
        
        for option in options:
            if not isinstance(option.value, str):
                raise RuntimeError(f'Key value is not of type str: "{option.value}" in {option}')
            elif not self._is_valid_key(option.value):
                raise RuntimeError(f'Key value is not a valid key: "{option.value}" in {option}. Valid keys include: {self.allowed_keys}')
            elif self._has_duplicate_keys(self.options):
                raise RuntimeError('Options cannot contain duplicate keys')

        self.selected_option: ClackOption = self.options[0]
        self.keys: list[str] = [option.value for option in self.options]
        self.render_frame: RenderFrame = RenderFrame()

        if not self.case_sensitive:
            self.keys = [key if key in self.special_allowed_keys else key.lower() for key in self.keys]

        self.abort_time = abort_time

        self.activate()

    def _all_options_disabled(self, options: list[ClackOption[str]]) -> bool:
        '''
        Check if all options are disabled.

        Args:
            options (list[ClackOption[str]]): A list of ClackOption objects.

        Returns:
            bool: True if all options are disabled, False otherwise.
        '''
        
        return all(option.disabled for option in self.options)

    def _is_valid_key(self, key: str) -> bool:
        '''
        Check if the given key is a valid input key.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key is valid, False otherwise.
        '''
        
        if key not in self.allowed_keys: return False
        return True

    def _construct_allowed_keys(self) -> tuple[str, ...]:
        '''
        Construct a tuple of allowed keys for the prompt.

        Returns:
            tuple[str]: A tuple of allowed keys.
        '''

        allowed_chars: tuple[str, ...] = tuple(chr(i) for i in range(33, 127))
        return self.special_allowed_keys + allowed_chars

    def _build_option_text(self, option: ClackOption[str], highlight: bool = False) -> Text:
        '''
        Build the text representation of an option.

        Args:
            option (ClackOption[str]): The option to build the text for.
            highlight (bool): Whether to highlight the option.

        Returns:
            Text: The text representation of the option.
        '''
        
        theme: Theme = get_active_theme()

        if not highlight:
            key_style: Style = copy(theme.text)
            key_style.bg_color = theme.muted.fg_color
        if highlight: key_style = copy(theme.cursor)
        if option.disabled:
            key_style.dim = True
            key_style.strikethrough = True

        value: str = f'[ {option.value} ]' if option.value in self.special_allowed_keys else option.value
        option_text: Text = Text.assemble(
            (f' {value} ', key_style), ' ',
            (option.label, theme.text if not option.disabled else theme.muted))
        if option.hint: option_text += Text(f' ({option.hint})', theme.muted)

        return option_text

    def _has_duplicate_keys(self, options: list[ClackOption[str]]) -> bool:
        '''
        Check if the options list contains duplicate keys.

        Args:
            options (list[ClackOption[str]]): A list of ClackOption objects.

        Returns:
            bool: True if there are duplicate keys, False otherwise.
        '''
        
        keys_list: list[str] = [option.value for option in options]
        if not self.case_sensitive: keys_list = [key.lower() for key in keys_list]
        keys_set: set[str] = set(keys_list)
        return len(keys_list) != len(keys_set)

    def _get_option_from_key(self, key: str, options: list[ClackOption[str]]) -> ClackOption[str] | None:
        '''
        Get the option corresponding to the given key.

        Args:
            key (str): The key to look for.
            options (list[ClackOption[str]]): A list of ClackOption objects.

        Returns:
            ClackOption[str] | None: The option corresponding to the key, or None if not found.
        '''
        
        for option in options:
            value = option.value
            if not self.case_sensitive and value not in self.special_allowed_keys:
                value = value.lower()
            if value == key:
                return option
        return None

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        
        if key is None: key = ''

        match key:
            case 'ENTER':
                if not self.options[0].disabled:
                    self.selected_option = self.options[0]
                    return True
            case _:
                if not self.case_sensitive and key not in self.special_allowed_keys: key = key.lower()
                    
                if key in self.keys:
                    selected_option: ClackOption | None = self._get_option_from_key(key, self.options)
                    if selected_option and not selected_option.disabled:
                        self.selected_option = selected_option
                        return True

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

        for i, option in enumerate(self.options):
            highlight: bool = True if i == 0 else False
            option_text: Text = self._build_option_text(option, highlight)
            option_lines: list[Text] = build_wrapped_lines(
                option_text,
                prefix_active)
            frame_builder.add_lines(*option_lines)

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

        selected_option: ClackOption = self.selected_option
        selected_option_label: str = selected_option.label if selected_option else 'None'
        selected_option_lines: list[Text] = build_wrapped_lines(
            Text(selected_option_label, theme.muted),
            prefix_muted)
        frame_builder.add_lines(*selected_option_lines)

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

        cancel_style: Style = copy(theme.muted)
        cancel_style.strikethrough = True
        selected_option_lines: list[Text] = build_wrapped_lines(
            Text(self.options[0].label, cancel_style),
            prefix_muted)
        frame_builder.add_lines(*selected_option_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        raise CancelException[ClackOption[str]](self.options[0])