from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
from typing import override, Optional
from ..config import get_active_theme
from .prompt_base import PromptBase
from ..terminal import Stdout

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
        '''

        self.title: str = title
        self.render_frame: RenderFrame = RenderFrame()

        super().__init__()
        super().activate()

    @override
    def _handle_active(self, _: Optional[str]) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        title_text: Text = Text(theme.symbols.connector_bar_start.resolve(), 
                                Text(f'  {self.title}', style=theme.text),
                                style=theme.active)
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.active)
        frame_builder.add_line(title_text)
        frame_builder.add_line(connector_text)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return True

    @override
    def _handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        title_text: Text = Text(theme.symbols.connector_bar_start.resolve(), 
                                Text(f'  {self.title}', style=theme.text),
                                style=theme.muted)
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.muted)
        frame_builder.add_line(title_text)
        frame_builder.add_line(connector_text)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True