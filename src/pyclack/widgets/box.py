from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.prompt_base import PromptBase, Alignment
from ..terminal import CursorController as cc
from ..prompts.util import build_box_lines
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override

def box(
    content: str,
    title: str = '',
    content_align: Alignment = Alignment.LEFT,
    title_align: Alignment = Alignment.LEFT,
    width: int | None = None,
    rounded: bool = True,
    title_padding: int = 1,
    content_padding: int = 2) -> None:
    '''
    Displays a customizable, fully-bordered box around text content, with an optional embedded title.

    Args:
        content (str): The text content shown inside the box.
        title (str): The title text embedded in the top border. Defaults to '' (no title).
        content_align (Alignment): Horizontal alignment of the content within the box. Defaults to Alignment.LEFT.
        title_align (Alignment): Horizontal alignment of the title within the top border. Defaults to Alignment.LEFT.
        width (int | None): Fixed total box width, or None to auto-fit the content/title. Defaults to None.
        rounded (bool): Use rounded corners when True, square corners when False. Defaults to True.
        title_padding (int): Number of spaces surrounding the title text. Defaults to 1.
        content_padding (int): Number of spaces surrounding content lines, on each side. Defaults to 2.
    '''

    Box(content, title, content_align, title_align, width, rounded, title_padding, content_padding)

class Box(PromptBase):
    '''
    A widget that renders a customizable, fully-bordered box around text
    content, with an optional embedded title.
    '''

    def __init__(self,
        content: str,
        title: str,
        content_align: Alignment,
        title_align: Alignment,
        width: int | None,
        rounded: bool,
        title_padding: int,
        content_padding: int):
        '''
        Initializes a Box instance.

        Args:
            content (str): The text content shown inside the box.
            title (str): The title text embedded in the top border.
            content_align (Alignment): Horizontal alignment of the content within the box.
            title_align (Alignment): Horizontal alignment of the title within the top border.
            width (int | None): Fixed total box width, or None to auto-fit the content/title.
            rounded (bool): Use rounded corners when True, square corners when False.
            title_padding (int): Number of spaces surrounding the title text.
            content_padding (int): Number of spaces surrounding content lines, on each side.
        '''

        super().__init__()

        self.content: str = content
        self.title: str = title
        self.content_align: Alignment = content_align
        self.title_align: Alignment = title_align
        self.width: int | None = width
        self.rounded: bool = rounded
        self.title_padding: int = title_padding
        self.content_padding: int = content_padding

        self.render_frame: RenderFrame = RenderFrame()

        self.activate()

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()

        if self.rounded:
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

        box_lines: list[Text] = build_box_lines(
            content=self.content,
            title=self.title,
            prefix=Text('', theme.text),
            content_style=theme.text,
            title_style=theme.muted,
            border_style=theme.muted,
            top_left_symbol=top_left,
            top_right_symbol=top_right,
            bottom_left_symbol=bottom_left,
            bottom_right_symbol=bottom_right,
            horizontal_bar_symbol=horizontal_bar,
            vertical_bar_symbol=vertical_bar,
            content_align=self.content_align,
            title_align=self.title_align,
            width=self.width,
            title_padding=self.title_padding,
            content_padding=self.content_padding)
        frame_builder.add_lines(*box_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True