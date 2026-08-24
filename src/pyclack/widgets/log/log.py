from ...prompts.util import build_wrapped_lines, build_message_header
from ...renderer import Text, Theme, FrameBuilder, RenderFrame
from ...terminal import CursorController as cc
from ...config import get_active_theme
from ...terminal import Stdout

class Log:
    '''
    A static class that provides methods to display various types of log messages in a structured format,
    including standard messages, informational messages, warnings, errors, and success notifications.
    '''

    @staticmethod
    def message(msg: str) -> None:
        '''
        Displays a standard message.

        Args:
            msg (str): The message to display.
        '''

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
        '''
        Displays an informational message.

        Args:
            msg (str): The informational message to display.
        '''

        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        log_level_info: str = theme.symbols.log_level_info.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        info_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{log_level_info}  ',
            theme.active,
            prefix_muted)
        frame_builder.add_lines(*info_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def warning(msg: str) -> None:
        '''
        Displays a warning message.

        Args:
            msg (str): The warning message to display.
        '''

        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        log_level_warn: str = theme.symbols.log_level_warn.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
        
        frame_builder.add_line(prefix_muted)
        warning_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{log_level_warn}  ',
            theme.error,
            prefix_muted)
        frame_builder.add_lines(*warning_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def warn(msg: str) -> None:
        '''
        Displays a warning message. This is an alias for the `warning` method.

        Args:
            msg (str): The warning message to display.
        '''

        Log.warning(msg)

    @staticmethod
    def error(msg: str) -> None:
        '''
        Displays an error message.

        Args:
            msg (str): The error message to display.
        '''

        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        log_level_error: str = theme.symbols.log_level_error.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        error_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{log_level_error}  ',
            theme.cancel,
            prefix_muted)
        frame_builder.add_lines(*error_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def success(msg: str) -> None:
        '''
        Displays a success message.

        Args:
            msg (str): The success message to display.
        '''

        Stdout.put(cc.hide_cursor())
    
        render_frame: RenderFrame = RenderFrame()
        frame_builder: FrameBuilder = FrameBuilder()
        
        theme: Theme = get_active_theme()
        connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
        log_level_success: str = theme.symbols.log_level_success.resolve()
        prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
    
        frame_builder.add_line(prefix_muted)
        success_lines: list[Text] = build_message_header(
            msg,
            theme.text,
            f'{log_level_success}  ',
            theme.submit,
            prefix_muted)
        frame_builder.add_lines(*success_lines)
    
        frame: tuple[Text, ...] = frame_builder.build()
        render_frame.draw_frame(*frame)
    
        Stdout.put(cc.show_cursor())

    @staticmethod
    def step(msg: str) -> None:
        '''
        Displays a step message, typically used to indicate progress in a multi-step process.

        Args:
            msg (str): The step message to display.
        '''

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