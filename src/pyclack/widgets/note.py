from ..renderer import Theme, RenderFrame, Text, FrameBuilder
from ..prompts.util import build_attached_box_lines
from ..terminal import CursorController as cc
from ..config import get_active_theme
from ..terminal import Stdout

def note(title: str, message: str) -> None:
    '''
    Displays a note to the user with a title and message.
    '''

    Stdout.put(cc.hide_cursor())
    
    render_frame: RenderFrame = RenderFrame()
    
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
        title=title,
        message=message,
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
    render_frame.draw_frame(*frame)

    Stdout.put(cc.show_cursor())