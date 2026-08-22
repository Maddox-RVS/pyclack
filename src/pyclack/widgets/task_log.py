from webbrowser import get

from ..prompts.util import build_message_header, build_wrapped_lines
from ..renderer import Text, Theme, FrameBuilder, RenderFrame
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout

class TaskLog():
    def __init__(self,
        title: str,
        limit: int | None = None,
        retain_log: bool = False) -> None:

        self._log: list[str] = [title]
        
        self._title: str = title
        self._limit: int | None = limit
        self._retain_log: bool = retain_log
        
        self._render_frame: RenderFrame = RenderFrame()
        self._buffer: list[list[Text]] = []

        self._is_success: bool = False

        self._render_title()

    def get_log(self) -> list[str]:
        return self._log

    def message(self, msg: str) -> None:
        if self._is_success: return
        
        message_lines: list[Text] = self._build_message(msg)
        self._buffer.append(message_lines)
        self._render()

        self._log.append(msg)
        if not self._retain_log and self._limit and len(self._log) > self._limit:
            self._log = self._log[-self._limit:]

    def success(self, msg: str) -> None:
        success_lines: list[Text] = self._build_success(msg)
        self._buffer = []
        self._buffer.append(success_lines)
        self._render()
        self._is_success = True

        self._log.append(msg)
        if not self._retain_log and self._limit and len(self._log) > self._limit:
            self._log = self._log[-self._limit:]

    def _render_title(self) -> None:
        theme: Theme = get_active_theme()

        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        title_lines: list[Text] = self._build_title()
        self._buffer.append(title_lines)
        self._buffer.append([prefix_muted])
        self._render()
        
    def _render(self) -> None:
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
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

        message_lines: list[Text] = build_wrapped_lines(Text(msg, theme.muted), prefix_muted)
        return message_lines

    def _build_success(self, msg: str) -> list[Text]:
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