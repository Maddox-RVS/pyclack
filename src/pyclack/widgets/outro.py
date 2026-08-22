from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..prompts.util import build_message_close
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout

def outro(message: str, custom_style: Style | None = None) -> None:
    '''
    Display an exit message.

    Args:
        message (str): The message to display to the user.
        custom_style (Style | None, optional): The custom style to use for the outro.
    '''
    
    Stdout.put(cc.hide_cursor())

    render_frame: RenderFrame = RenderFrame()
    
    theme: Theme = get_active_theme()
    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    connector_bar_end: str = theme.symbols.connector_bar_end.resolve()
    prefix: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    closing_prefix: Text = Text(f'{connector_bar_end}  ', theme.muted)

    text_style: Style = custom_style if custom_style else theme.text
    frame_builder: FrameBuilder = FrameBuilder()
    frame_builder.add_line(prefix)
    outro_text_lines: list[Text] = build_message_close(message, text_style, prefix, closing_prefix)
    frame_builder.add_lines(*outro_text_lines)
    frame: tuple[Text, ...] = frame_builder.build()
    render_frame.draw_frame(*frame)

    Stdout.put(cc.show_cursor())