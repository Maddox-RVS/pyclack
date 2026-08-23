from ..prompts.util import build_message_header, build_wrapped_lines
from ..renderer import Text, Theme, FrameBuilder, RenderFrame
from ..terminal import CursorController as cc
from ..prompts import CancelException
from ..config import get_active_theme
from ..terminal import Stdout
import signal

class TaskLog():
    '''
    A class that manages and displays a log of messages in a structured format, with support for titles, 
    message limits, and success states.
    '''

    def __init__(self,
        title: str,
        limit: int | None = None,
        retain_log: bool = False) -> None:
        '''
        Initializes a TaskLog instance.

        Args:
            title (str): The title of the task log.
            limit (int | None): The maximum number of messages to keep in the log. If None, no limit is applied. Defaults to None.
            retain_log (bool): Whether to retain the log history instead of clearing it to limit if one is set. Defaults to False.
        '''

        self._log: list[str] = [title]
        
        self._title: str = title
        self._limit: int | None = limit
        self._retain_log: bool = retain_log
        
        self._render_frame: RenderFrame = RenderFrame()
        self._buffer: list[list[Text]] = []

        self._is_success: bool = False

        self._render_title()

        self._has_message: bool = False

    def get_log(self) -> list[str]:
        '''
        Returns the current log of messages.

        Returns:
            list[str]: The list of messages in the log.
        '''

        return self._log

    def message(self, msg: str) -> None:
        '''
        Adds a message to the log.

        Args:
            msg (str): The message to add to the log.
        '''

        if self._is_success: return

        if not self._has_message:
            self._old_sigint_handler = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self._handle_interrupt)
        self._has_message = True
        
        message_lines: list[Text] = self._build_message(msg)
        self._buffer.append(message_lines)
        self._render()

        self._log.append(msg)
        if not self._retain_log and self._limit and len(self._log) > self._limit:
            self._log = self._log[-self._limit:]

    def success(self, msg: str) -> None:
        '''
        Marks the task as successful, adds a success message to the log, and renders it.

        Args:
            msg (str): The success message to add to the log.
        '''

        success_lines: list[Text] = self._build_success(msg)
        self._buffer = []
        self._buffer.append(success_lines)
        self._render()
        self._is_success = True

        self._log.append(msg)
        if not self._retain_log and self._limit and len(self._log) > self._limit:
            self._log = self._log[-self._limit:]

        signal.signal(signal.SIGINT, self._old_sigint_handler)

    def _handle_interrupt(self, signum, frame):
        '''
        Handles the SIGINT signal (Ctrl+C) to cancel the TaskLog and raise a CancelException.
        '''

        signal.signal(signal.SIGINT, self._old_sigint_handler)
        raise CancelException

    def _render_title(self) -> None:
        '''
        Renders the title of the task log at the top of the log display.
        '''

        theme: Theme = get_active_theme()

        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        title_lines: list[Text] = self._build_title()
        self._buffer.append(title_lines)
        self._buffer.append([prefix_muted])
        self._render()
        
    def _render(self) -> None:
        '''
        Renders the current state of the task log, including the title and all messages, to the terminal.
        This method handles the display of the log, ensuring that it respects the message limit and formatting.
        '''

        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        frame_builder: FrameBuilder = FrameBuilder()
        frame_builder.add_line(prefix_muted)
        buffer: list[list[Text]] = self._buffer
        if self._limit and len(buffer) > self._limit + 2:
            messages = buffer[2:]
            buffer = buffer[:2] + messages[-self._limit:]
        lines: list[Text] = []
        for group in buffer:
            for line in group:
                lines.append(line)
        frame_builder.add_lines(*lines)
        
        frame: tuple[Text, ...] = frame_builder.build()
        self._render_frame.draw_frame(*frame)
        
        Stdout.put(cc.show_cursor())

    def _build_title(self) -> list[Text]:
        '''
        Builds the title section of the task log, including the title text and any associated formatting.

        Returns:
            list[Text]: A list of Text objects representing the title lines to be rendered.
        '''

        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        title_lines: list[Text] = build_message_header(
            self._title,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        return title_lines

    def _build_message(self, msg: str) -> list[Text]:
        '''
        Builds the message section of the task log, formatting the message text and applying any necessary wrapping.

        Args:
            msg (str): The message text to format and wrap.

        Returns:
            list[Text]: A list of Text objects representing the message lines to be rendered.
        '''

        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        message_lines: list[Text] = build_wrapped_lines(Text(msg, theme.muted), prefix_muted)
        return message_lines

    def _build_success(self, msg: str) -> list[Text]:
        '''
        Builds the success message section of the task log, formatting the success message text and 
        applying any necessary wrapping.

        Args:
            msg (str): The success message text to format and wrap.

        Returns:
            list[Text]: A list of Text objects representing the success message lines to be rendered.
        '''
        
        theme: Theme = get_active_theme()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        success_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{step_marker_active}  ',
            theme.submit,
            prefix_muted)
        return success_lines