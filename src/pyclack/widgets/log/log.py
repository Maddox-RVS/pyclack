from ...prompts.util import build_wrapped_lines, build_message_header
from ...renderer import Text, Theme, FrameBuilder, RenderFrame
from ...terminal import CursorController as cc
from ...config import get_active_theme
from ...terminal import Stdout

class Log:

    @staticmethod
    def message(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        message_lines: list[Text] = build_wrapped_lines(Text(msg, theme.text), prefix_muted)
        frame_builder.add_lines(*message_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def info(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        selection_widget_radio_active: str = theme.symbols.selection_widget_radio_active.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        info_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{selection_widget_radio_active}  ',
            theme.active,
            prefix_muted)
        frame_builder.add_lines(*info_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def warning(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        step_marker_error: str = theme.symbols.step_marker_error.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        frame_builder.add_line(prefix_muted)
        warning_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{step_marker_error}  ',
            theme.error,
            prefix_muted)
        frame_builder.add_lines(*warning_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def warn(msg: str) -> None:
        Log.warning(msg)

    @staticmethod
    def error(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        error_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{step_marker_cancel}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*error_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def success(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        step_marker_active: str = theme.symbols.step_marker_active.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        success_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{step_marker_active}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*success_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def step(msg: str) -> None:
        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        frame_builder.add_line(prefix_muted)
        step_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{step_marker_submit}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*step_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())