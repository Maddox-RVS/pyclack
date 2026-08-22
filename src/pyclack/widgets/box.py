from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.prompt_base import Alignment
from ..terminal import CursorController as cc
from ..prompts.util import build_box_lines
from ..config import get_active_theme
from ..terminal import Stdout

def box(
    content: str,
    title: str = '',
    content_align: Alignment = Alignment.LEFT,
    title_align: Alignment = Alignment.LEFT,
    width: int | None = None,
    rounded: bool = True,
    title_padding: int = 0,
    content_padding: int = 2) -> None:
    '''
    Displays a customizable, fully-bordered box around text content, with an optional embedded title.

    Args:
        content (str): The text content shown inside the box.
        title (str): The title text embedded in the top border. Defaults to '' (no title).
        content_align (Alignment): Horizontal alignment of the content within the box. Defaults to Alignment.LEFT.
        title_align (Alignment): Horizontal alignment of the title within the top border. Defaults to Alignment.LEFT.
        width (int | None): Fixed total box width, or None to auto-fit the content/title up to the terminal's width. Defaults to None.
        rounded (bool): Use rounded corners when True, square corners when False. Defaults to True.
        title_padding (int): Number of spaces surrounding the title text. Defaults to 1.
        content_padding (int): Number of spaces surrounding content lines, on each side. Defaults to 2.
    '''

    Stdout.put(cc.hide_cursor())

    render_frame: RenderFrame = RenderFrame()

    theme: Theme = get_active_theme()

    connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
    prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

    if rounded:
        top_left = theme.symbols.box_drawing_top_left_corner_rounded.resolve()
        top_right = theme.symbols.box_drawing_top_right_corner_rounded.resolve()
        bottom_left = theme.symbols.box_drawing_bottom_left_corner_rounded.resolve()
        bottom_right = theme.symbols.box_drawing_bottom_right_corner_rounded.resolve()
    else:
        top_left = theme.symbols.box_drawing_top_left_corner.resolve()
        top_right = theme.symbols.box_drawing_top_right_corner.resolve()
        bottom_left = theme.symbols.box_drawing_bottom_left_corner.resolve()
        bottom_right = theme.symbols.box_drawing_bottom_right_corner.resolve()

    horizontal_bar = theme.symbols.box_drawing_horizontal_bar.resolve()
    vertical_bar = theme.symbols.connector_bar_vertical.resolve()

    frame_builder: FrameBuilder = FrameBuilder()

    frame_builder.add_line(prefix_muted)

    box_lines: list[Text] = build_box_lines(
        content=content,
        title=title,
        prefix=prefix_muted,
        content_style=theme.text,
        title_style=theme.muted,
        border_style=theme.muted,
        top_left_symbol=top_left,
        top_right_symbol=top_right,
        bottom_left_symbol=bottom_left,
        bottom_right_symbol=bottom_right,
        horizontal_bar_symbol=horizontal_bar,
        vertical_bar_symbol=vertical_bar,
        content_align=content_align,
        title_align=title_align,
        width=width,
        title_padding=title_padding,
        content_padding=content_padding)
    frame_builder.add_lines(*box_lines)

    frame: tuple[Text, ...] = frame_builder.build()
    render_frame.draw_frame(*frame)

    Stdout.put(cc.show_cursor())