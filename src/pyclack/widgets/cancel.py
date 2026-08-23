from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.util import build_message_close
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout

def cancel(message: str) -> None:
    '''
    Display a cancellation message to the user.

    Args:
        message (str): The cancellation message to display.
    '''
    
    Stdout.put(cc.hide_cursor())
    
    render_frame: RenderFrame = RenderFrame()
    
    theme: Theme = get_active_theme()
    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
    prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    closing_prefix_muted: Text = Text(f'{connector_bar_end}  ', theme.muted)

    frame_builder: FrameBuilder = FrameBuilder()
    frame_builder.add_line(prefix_muted)
    cancel_lines: list[Text] = build_message_close(
        message,
        theme.cancel,
        prefix_muted,
        closing_prefix_muted)
    frame_builder.add_lines(*cancel_lines)

    frame: tuple[Text, ...] = frame_builder.build()
    render_frame.draw_frame(*frame)

    Stdout.put(cc.show_cursor())