from ..renderer import Theme, RenderFrame, Text, FrameBuilder, Style
from ..prompts.util import build_message_open
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from typing import override, Optional
from ..config import get_active_theme
from ..terminal import Stdout

def intro(title: str, custom_style: Optional[Style] = None) -> None:
    '''
    Display an introductory message with a title.

    Args:
        title (str): The title to display to the user.
        custom_style (Optional[Style]): The custom style to use for the intro.
    '''
    
    Intro(title, custom_style)

class Intro(PromptBase):
    '''
    A class to display an introductory message with a title.
    '''

    def __init__(self, title: str, custom_style: Optional[Style] = None):
        '''
        Initialize an Intro prompt with the given title.

        Args:
            title (str): The title to display to the user.
            custom_style (Optional[Style]): The custom style to use for the intro.
        '''

        self.title: str = title
        self.custom_style: Optional[Style] = custom_style
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        connector_bar_start: str = theme.symbols.connector_bar_start.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        opening_prefix: Text = Text(f'{connector_bar_start}  ', theme.muted)

        text_style: Style = self.custom_style if self.custom_style else theme.text
        frame_builder: FrameBuilder = FrameBuilder()
        title_text_lines: list[Text] = build_message_open(self.title, text_style, prefix, opening_prefix)
        frame_builder.add_lines(*title_text_lines)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True