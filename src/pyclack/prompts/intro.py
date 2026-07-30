from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
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

        super().__init__(
            self._handle_active,
            self._handle_submit,
            self._handle_error,
            self._handle_cancel
        )

        self.title: str = title
        self.render_frame: RenderFrame = RenderFrame()

        super().activate()

    def _handle_active(self, _: str) -> bool:
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

    def _handle_error(self, _: str) -> bool: pass
    def _handle_cancel(self) -> None: pass