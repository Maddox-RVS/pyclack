from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..prompts.util import build_message_open
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout

def intro(title: str, custom_style: Style | None = None) -> None:
    '''
    Display an introductory message with a title.

    Args:
        title (str): The title to display to the user.
        custom_style (Style | None, optional): The custom style to use for the intro.
    '''

    Stdout.put(cc.hide_cursor())
       
    render_frame: RenderFrame = RenderFrame()
            
    theme: Theme = get_active_theme()
    connector_bar_start: str = theme.symbols.connector_bar_start.resolve()
    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    prefix: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    opening_prefix: Text = Text(f'{connector_bar_start}  ', theme.muted)

    text_style: Style = custom_style if custom_style else theme.text
    frame_builder: FrameBuilder = FrameBuilder()
    title_text_lines: list[Text] = build_message_open(title, text_style, prefix, opening_prefix)
    frame_builder.add_lines(*title_text_lines)
    frame: tuple[Text, ...] = frame_builder.build()
    render_frame.draw_frame(*frame)

    Stdout.put(cc.show_cursor())