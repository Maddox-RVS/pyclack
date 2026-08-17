from ..prompts.util import build_wrapped_lines, build_message_header, build_message_close
from ..renderer import Text, RenderFrame, FrameBuilder, Theme, Style
from ..prompts import PromptBase, CancelException
from ..terminal import CursorController as cc
from ..config import get_active_theme
from datetime import date as ddate
from ..terminal import Stdout
from typing import Callable
from copy import copy
import calendar

def date(message: str,
        initial_date: ddate,
        min_date: ddate,
        max_date: ddate,
        cancellation_message: str = 'Operation Cancelled',
        show_cancellation_message: bool = True,
        validate: Callable[[ddate], str | None] | None = None,
        abort_time: float | None = None) -> ddate:
    '''
    Ask the user to select a date within a specified range.
    Controls are as follows:
    - Use the arrow keys or 'h', 'j', 'k', 'l' to navigate between the month, day, and year fields.
    - Use the up and down arrow keys or 'j' and 'k' to increase or decrease the value of the selected field.
    - Type numbers to input values directly into the selected field.
    - Press 'Enter' to submit the selected date.
    - Press 'Tab' to move to the next field.
    - Press 'Backspace' to clear the selected field or move to the previous field if it is already empty.
    - Press 'Ctrl+C' or 'esc' to cancel the prompt.

    Args:
        message (str): The message to display to the user.
        initial_date (ddate): The initial date to display in the prompt.
        min_date (ddate): The minimum date that can be selected.
        max_date (ddate): The maximum date that can be selected.
        cancellation_message (str, optional): The message to display if the user cancels the operation.
        show_cancellation_message (bool, optional): If True shows cancellation message, shows no cancellation message if False. Defaults to True.
        validate (Callable[[ddate], str | None], optional): A function that takes a date and returns an error message if the date is invalid, or None if the date is valid.
        abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

    Returns:
        ddate: The date selected by the user.

    Raises:
        CancelException: If the user cancels the operation.
    '''

    prompt: Date = Date(message, initial_date, min_date, max_date, cancellation_message, validate, show_cancellation_message, abort_time)
    return ddate(int(prompt.date_buffer[2]), int(prompt.date_buffer[0]), int(prompt.date_buffer[1]))

class Date(PromptBase):
    '''
    A prompt for selecting a date within a specified range.
    '''

    def __init__(self,
                message: str,
                initial_date: ddate,
                min_date: ddate,
                max_date: ddate,
                cancellation_message: str,
                validate: Callable[[ddate], str | None] | None,
                show_cancellation_message: bool,
                abort_time: float | None):
        '''
        Initialize a Date prompt.

        Args:
            message (str): The message to display to the user.
            initial_date (ddate): The initial date to display in the prompt.
            min_date (ddate): The minimum date that can be selected.
            max_date (ddate): The maximum date that can be selected.
            cancellation_message (str): The message to display if the user cancels the operation.
            validate (Callable[[ddate], str | None]): A function that takes a date and returns an error message if the date is invalid, or None if the date is valid.
            show_cancellation_message (bool): If True shows cancellation message, shows no cancellation message if False. Defaults to True.
            abort_time (float): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.

        Raises:
            CancelException: If the user cancels the operation.
        '''

        super().__init__()

        self.message: str = message
        self.initial_date: ddate = initial_date
        self.min_date: ddate = min_date
        self.max_date: ddate = max_date
        self.cancellation_message: str = cancellation_message
        self.show_cancellation_message: bool = show_cancellation_message
        self.validate: Callable[[ddate], str | None] | None = validate

        self.date_buffer: list[str] = [str(self.initial_date.month),
                                        str(self.initial_date.day),
                                        str(self.initial_date.year)]
        self.date_index: int = 0

        self.propogate_key_after_error = True
        self.abort_time = abort_time
        self.allowed_inputs: tuple[str, ...] = self._construct_allowed_inputs()
        self.render_frame: RenderFrame = RenderFrame()

        super().activate()

    def _validate(self) -> str | None:
        '''
        Validate the current date input buffer and return an error message if the date is invalid, or None if the date is valid.

        Returns:
            str | None: An error message if the date is invalid, or None if the date is valid.
        '''

        if not (len(self.date_buffer[0]) > 0 and len(self.date_buffer[1]) > 0 and len(self.date_buffer[2]) > 0):
            return 'Date must be complete'

        try:
            inputted_date: ddate = ddate(int(self.date_buffer[2]), int(self.date_buffer[0]), int(self.date_buffer[1]))
            if inputted_date < self.min_date: return f'Date must be on or after {self.min_date.strftime('%Y-%m-%d')}'
            elif inputted_date > self.max_date: return f'Date must be on or before {self.max_date.strftime('%Y-%m-%d')}'
            else: return self.validate(inputted_date) if self.validate else None
        except Exception: return 'Something is wrong with this input! Please use mm/dd/yyyy format, and valid date ranges!'

    def _selection_left(self) -> None:
        '''
        Move the selection index to the left.
        '''

        self.date_index = max(0, self.date_index - 1)

    def _selection_right(self) -> None:
        '''
        Move the selection index to the right.
        '''

        self.date_index = min(2, self.date_index + 1)

    def _selection_increase(self) -> None:
        '''
        Increase the value of the currently selected date field.
        '''

        current_raw: str = self.date_buffer[self.date_index]
        is_blank: bool = current_raw == ''
        num: int = int(current_raw) if current_raw else 0

        month: int = int(self.date_buffer[0]) if self.date_buffer[0] else 0
        year: int = int(self.date_buffer[2]) if self.date_buffer[2] else 0

        if self.date_index == 2:
            bounds_min = self.min_date.year
            bounds_max = self.max_date.year
        elif self.date_index == 0:
            bounds_min = self.min_date.month if year == self.min_date.year else 1
            bounds_max = self.max_date.month if year == self.max_date.year else 12
        else:
            def days_in_month(y: int, m: int) -> int:
                return calendar.monthrange(y or 2001, m or 1)[1]

            bounds_min = self.min_date.day if (year == self.min_date.year and month == self.min_date.month) else 1
            bounds_max = self.max_date.day if (year == self.max_date.year and month == self.max_date.month) else days_in_month(year, month)

        next_value: int = bounds_min if is_blank else max(bounds_min, min(bounds_max, num + 1))
        self.date_buffer[self.date_index] = str(next_value)

    def _selection_decrease(self) -> None:
        '''
        Decrease the value of the currently selected date field.
        '''

        current_raw: str = self.date_buffer[self.date_index]
        is_blank: bool = current_raw == ''
        num: int = int(current_raw) if current_raw else 0

        month: int = int(self.date_buffer[0]) if self.date_buffer[0] else 0
        year: int = int(self.date_buffer[2]) if self.date_buffer[2] else 0

        if self.date_index == 2:
            bounds_min = self.min_date.year
            bounds_max = self.max_date.year
        elif self.date_index == 0:
            bounds_min = self.min_date.month if year == self.min_date.year else 1
            bounds_max = self.max_date.month if year == self.max_date.year else 12
        else:
            def days_in_month(y: int, m: int) -> int:
                return calendar.monthrange(y or 2001, m or 1)[1]

            bounds_min = self.min_date.day if (year == self.min_date.year and month == self.min_date.month) else 1
            bounds_max = self.max_date.day if (year == self.max_date.year and month == self.max_date.month) else days_in_month(year, month)

        next_value: int = bounds_max if is_blank else max(bounds_min, min(bounds_max, num - 1))
        self.date_buffer[self.date_index] = str(next_value)

    def _add_str(self, original: str, new: str, max_chars: int) -> str:
        '''
        Add a new string to the original string, ensuring that the total length does not exceed max_chars.

        Args:
            original (str): The original string.
            new (str): The new string to add.
            max_chars (int): The maximum allowed length of the resulting string.

        Returns:
            str: The resulting string after adding the new string, or the original string if the total length exceeds max_chars.
        '''

        if len(original) + len(new) > max_chars: return original
        else: return original + new

    def _construct_allowed_inputs(self) -> tuple[str, ...]:
        '''
        Construct a tuple of allowed inputs for the prompt.

        Returns:
            tuple[str]: A tuple of allowed input keys.
        '''

        allowed_chars: tuple[str, ...] = tuple(str(i) for i in range(10))
        return ('BACKSPACE',
                'TAB',
                'ENTER',
                'LEFT', 'RIGHT', 'UP', 'DOWN',
                'h', 'j', 'k', 'l', 'H', 'J', 'K', 'L') + allowed_chars

    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        if key not in self.allowed_inputs: key = ''

        match key:
            case 'BACKSPACE':
                if len(self.date_buffer[self.date_index]) > 0: self.date_buffer[self.date_index] = ''
                else: self._selection_left() 
            case 'TAB': self._selection_right()
            case 'ENTER': return True # Advance to the next state (submit)
            case 'LEFT' | 'h' | 'H': self._selection_left()
            case 'RIGHT' | 'l' | 'L': self._selection_right()
            case 'UP' | 'k' | 'K': self._selection_increase()
            case 'DOWN' | 'j' | 'J': self._selection_decrease()
            case '': pass
            case _:
                current_input: str = self.date_buffer[self.date_index]
                max_chars: int = 2 if (self.date_index == 0 or self.date_index == 1) else 4
                new_buffer: str = self._add_str(current_input, key, max_chars)
                if self.date_buffer[self.date_index] == new_buffer:
                    self._selection_right()
                    current_input = self.date_buffer[self.date_index]
                    max_chars = 2 if (self.date_index == 0 or self.date_index == 1) else 4
                    new_buffer = self._add_str(current_input, key, max_chars)
                    self.date_buffer[self.date_index] = new_buffer
                else: self.date_buffer[self.date_index] = new_buffer

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_active}  ',
            theme.active,
            prefix_active)
        frame_builder.add_lines(*message_lines)

        month: str = self.date_buffer[0]
        day: str = self.date_buffer[1]
        year: str = self.date_buffer[2]

        if month != '': month = '0' * (2 - len(month)) + month
        if day != '': day = '0' * (2 - len(day)) + day
        if year != '': year = '0' * (4 - len(year)) + year

        month_text: Text = Text(month, theme.text) if len(month) > 0 else Text('mm', theme.muted)
        day_text: Text = Text(day, theme.text) if len(day) > 0 else Text('dd', theme.muted)
        year_text: Text = Text(year, theme.text) if len(year) > 0 else Text('yyyy', theme.muted)

        if self.date_index == 0: month_text.style = theme.cursor
        elif self.date_index == 1: day_text.style = theme.cursor
        elif self.date_index == 2: year_text.style = theme.cursor

        date_selector_text: Text = Text.assemble(
            prefix_active,
            month_text,
            ('/', theme.muted),
            day_text,
            ('/', theme.muted),
            year_text)
        frame_builder.add_line(date_selector_text)

        frame_builder.add_line(Text(connector_bar_end, theme.active))

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return False

    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        month: str = self.date_buffer[0]
        day: str = self.date_buffer[1]
        year: str = self.date_buffer[2]

        if month != '': month = '0' * (2 - len(month)) + month
        if day != '': day = '0' * (2 - len(day)) + day
        if year != '': year = '0' * (4 - len(year)) + year

        month_text: Text = Text(month, theme.muted) if len(month) > 0 else Text('mm', theme.muted)
        day_text: Text = Text(day, theme.muted) if len(day) > 0 else Text('dd', theme.muted)
        year_text: Text = Text(year, theme.muted) if len(year) > 0 else Text('yyyy', theme.muted)

        date_selector_text: Text = Text.assemble(
            prefix_muted,
            month_text,
            ('/', theme.muted),
            day_text,
            ('/', theme.muted),
            year_text)
        frame_builder.add_line(date_selector_text)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        Stdout.put(cc.show_cursor())
        return False if self._validate() else True

    def handle_error(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        prefix_error: Text = Text(f'{connector_bar_vertical}  ', theme.error)
        closing_prefix_error: Text = Text(f'{connector_bar_end}  ', theme.error)

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_error}  ',
            theme.error,
            prefix_error)
        frame_builder.add_lines(*message_lines)

        month: str = self.date_buffer[0]
        day: str = self.date_buffer[1]
        year: str = self.date_buffer[2]

        if month != '': month = '0' * (2 - len(month)) + month
        if day != '': day = '0' * (2 - len(day)) + day
        if year != '': year = '0' * (4 - len(year)) + year

        month_text: Text = Text(month, theme.text) if len(month) > 0 else Text('mm', theme.muted)
        day_text: Text = Text(day, theme.text) if len(day) > 0 else Text('dd', theme.muted)
        year_text: Text = Text(year, theme.text) if len(year) > 0 else Text('yyyy', theme.muted)

        if self.date_index == 0: month_text.style = theme.cursor
        elif self.date_index == 1: day_text.style = theme.cursor
        elif self.date_index == 2: year_text.style = theme.cursor

        date_selector_text: Text = Text.assemble(
            prefix_error,
            month_text,
            ('/', theme.muted),
            day_text,
            ('/', theme.muted),
            year_text)
        frame_builder.add_line(date_selector_text)

        error_message: str = self._validate() # self.validate must be defined if we are in the error state, and it must return something
        error_lines: list[Text] = build_message_close(
            error_message,
            theme.error,
            prefix_error,
            closing_prefix_error)
        frame_builder.add_lines(*error_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        if key in self.allowed_inputs: return True
        else: return False

    def handle_cancel(self):
        theme: Theme = get_active_theme()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

        # Create and render next frame based on the current input buffer and state
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        message_lines: list[Text] = build_message_header(
            self.message,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*message_lines)

        month: str = self.date_buffer[0]
        day: str = self.date_buffer[1]
        year: str = self.date_buffer[2]

        if month != '': month = '0' * (2 - len(month)) + month
        if day != '': day = '0' * (2 - len(day)) + day
        if year != '': year = '0' * (4 - len(year)) + year

        text_style: Style = copy(theme.muted)
        text_style.strikethrough = True
        month_text: Text = Text(month, text_style) if len(month) > 0 else Text('mm', text_style)
        day_text: Text = Text(day, text_style) if len(day) > 0 else Text('dd', text_style)
        year_text: Text = Text(year, text_style) if len(year) > 0 else Text('yyyy', text_style)

        date_selector_text: Text = Text.assemble(
            prefix_muted,
            month_text,
            ('/', text_style),
            day_text,
            ('/', text_style),
            year_text)
        frame_builder.add_line(date_selector_text)

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
        raise CancelException(self.cancellation_message,
            f'{year_text.get_raw_isolated_text()}-{month_text.get_raw_isolated_text()}-{day_text.get_raw_isolated_text()}')
