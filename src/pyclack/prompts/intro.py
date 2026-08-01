from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
from .util import build_wrapped_input_lines
from ..config import get_active_theme
from .prompt_base import PromptBase
from ..terminal import Stdout
from typing import override

def intro(title: str) -> None:
    '''
    Display an introductory message with a title.
    '''
    
    Intro(title)

class Intro(PromptBase):
    '''
    A class to display an introductory message with a title.
    '''

    def __init__(self, title: str):
        '''
        Initialize an Intro prompt with the given title.

        Args:
            title (str): The title to display to the user.
        '''

        self.title: str = title
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        title_text_lines: list[Text] = build_wrapped_input_lines(self.title, 0, theme.text, theme.muted)
        title_text_lines[0] = Text(theme.symbols.connector_bar_start.resolve(), Text(title_text_lines[0].get_raw_text()[1:], style=theme.text), style=theme.muted)
        for line in title_text_lines: frame_builder.add_line(line)
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.muted)
        frame_builder.add_line(connector_text)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True