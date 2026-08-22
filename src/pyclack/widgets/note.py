from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.util import build_attached_box_lines
from ..terminal import CursorController as cc
from ..prompts.prompt_base import PromptBase
from ..config import get_active_theme
from ..terminal import Stdout
from typing import override

def note(title: str, message: str) -> None:
    '''
    Displays a note to the user with a title and message.
    '''

    Note(title, message)

class Note(PromptBase):
    '''
    A class that displays a note to the user with a title and message.
    '''

    def __init__(self, title: str, message: str):
        '''
        Initializes a Note instance.

        Args:
            title (str): The title of the note.
            message (str): The message of the note.
        '''

        super().__init__()

        self.title: str = title
        self.message: str = message

        self.render_frame: RenderFrame = RenderFrame()
        
        self.activate()

    @override
    def handle_active(self, key: str | None) -> bool:
        Stdout.put(cc.hide_cursor())
        
        theme: Theme = get_active_theme()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        box_drawing_bottom_right_corner_rounded: str = theme.symbols.box_drawing_bottom_right_corner_rounded.resolve()
        box_drawing_horizontal_bar: str = theme.symbols.box_drawing_horizontal_bar.resolve()
        box_drawing_left_connector: str = theme.symbols.box_drawing_left_connector.resolve()
        box_drawing_top_right_corner_rounded: str = theme.symbols.box_drawing_top_right_corner_rounded.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(prefix_muted)

        box_lines: list[Text] = build_attached_box_lines(
            title=self.title,
            message=self.message,
            prefix=prefix_muted,
            title_marker_prefix=Text(f'{step_marker_submit}  ', theme.submit),
            title_style=theme.text,
            message_style=theme.text,
            border_style=theme.muted,
            right_bar_symbol=connector_bar_vertical,
            horizontal_bar_symbol=box_drawing_horizontal_bar,
            left_connector_symbol=box_drawing_left_connector,
            top_right_corner_symbol=box_drawing_top_right_corner_rounded,
            bottom_right_corner_symbol=box_drawing_bottom_right_corner_rounded)
        frame_builder.add_lines(*box_lines)

        frame: tuple[Text, ...] = frame_builder.build()
        self.render_frame.draw_frame(*frame)

        Stdout.put(cc.show_cursor())
        return True