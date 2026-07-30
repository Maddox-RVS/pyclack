from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..terminal import CursorController as cc
from ..config import get_active_theme
from .prompt_base import PromptBase
from .. terminal import Stdout

def outro(message: str) -> None:
    '''
    Display an exit message.
    '''
    
    Outro(message)

class Outro(PromptBase):
    '''
    A class to display an exit message.
    '''

    def __init__(self, message: str):
        '''
        Initialize an Outro prompt with the given message.
        '''

        super().__init__(
            self._handle_active,
            self._handle_submit,
            self._handle_error,
            self._handle_cancel
        )

        self.message: str = message
        self.render_frame: RenderFrame = RenderFrame()

        super().activate()

    def _handle_active(self, _: str) -> bool:
        Stdout.put(cc.hide_cursor())

        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.active)
        outro_text: Text = Text(theme.symbols.connector_bar_end.resolve(), 
                                Text(f'  {self.message}', style=theme.text),
                            style=theme.active)
        frame_builder.add_line(connector_text)
        frame_builder.add_line(outro_text)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)
        return True

    def _handle_submit(self) -> bool:
        theme: Theme = get_active_theme()
        frame_builder: FrameBuilder = FrameBuilder()
        connector_text: Text = Text(theme.symbols.connector_bar_vertical.resolve(), style=theme.muted)
        outro_text: Text = Text(theme.symbols.connector_bar_end.resolve(), 
                                Text(f'  {self.message}', style=theme.text),
                            style=theme.muted)
        frame_builder.add_line(connector_text)
        frame_builder.add_line(outro_text)
        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True

    def _handle_error(self, _: str) -> bool: pass
    def _handle_cancel(self) -> None: pass