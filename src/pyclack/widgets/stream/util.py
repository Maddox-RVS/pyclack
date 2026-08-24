from ...renderer import Text, Theme, FrameBuilder, RenderFrame, Style
from collections.abc import Iterable, AsyncIterable
from ...prompts.util import build_message_header
from ...terminal import CursorController as cc
from ...terminal import Stdout, EchoController
from ...prompts import CancelException
from ...config import get_active_theme
import asyncio
import signal

def render_iterable(iterable: Iterable[str] | AsyncIterable[str], step_marker_prefix: str, step_marker_prefix_style: Style) -> None:

    # Terminal state
    old_sigint_handler = signal.getsignal(signal.SIGINT)
    def handle_interrupt(signum, frame) -> None:
        signal.signal(signal.SIGINT, old_sigint_handler)
        EchoController.enable_ctl_echo()
        raise CancelException
    signal.signal(signal.SIGINT, handle_interrupt)
    if EchoController.is_ctl_echo_enabled():
        EchoController.disable_ctl_echo()
    Stdout.put(cc.hide_cursor())

    # Rendering
    render_frame: RenderFrame = RenderFrame()
    frame_builder: FrameBuilder = FrameBuilder()

    theme: Theme = get_active_theme()
    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

    text: str = ''
    
    if isinstance(iterable, Iterable):
        for item in iterable:
            text += item
            text_lines: list[Text] = build_message_header(
                text,
                theme.text,
                step_marker_prefix,
                step_marker_prefix_style,
                prefix_muted)
            frame_builder.add_line(prefix_muted)
            frame_builder.add_lines(*text_lines)
            frame: tuple[Text, ...] = frame_builder.build()
            render_frame.draw_frame(*frame)
            frame_builder.clear()
    elif isinstance(iterable, AsyncIterable):
        async def consume() -> None:
            nonlocal text
            async for item in iterable:
                text += item
                text_lines: list[Text] = build_message_header(
                    text,
                    theme.text,
                    step_marker_prefix,
                    step_marker_prefix_style,
                    prefix_muted)
                frame_builder.add_line(prefix_muted)
                frame_builder.add_lines(*text_lines)
                frame: tuple[Text, ...] = frame_builder.build()
                render_frame.draw_frame(*frame)
                frame_builder.clear()
        asyncio.run(consume())
    else: 
        signal.signal(signal.SIGINT, old_sigint_handler)
        EchoController.enable_ctl_echo()
        raise ValueError(f'Expected "Iterable" or "AsyncIterable" but got {type(iterable)}')

    # Terminal state
    signal.signal(signal.SIGINT, old_sigint_handler)
    EchoController.enable_ctl_echo()
    Stdout.put(cc.show_cursor())