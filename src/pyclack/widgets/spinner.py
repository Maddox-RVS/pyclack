from ..renderer import Text, Theme, FrameBuilder, RenderFrame, SpinnerSymbols
from ..prompts.util import build_message_header, build_wrapped_lines
from ..terminal import CursorController as cc
from ..terminal import Stdout, EchoController
from ..prompts import CancelException
from ..config import get_active_theme
from threading import Thread, Event
import signal
import time

class Spinner:
    '''
    A terminal spinner that displays a message with an animated spinner, optional ellipsis, and optional timer.
    '''

    def __init__(self,
        show_timer: bool = False,
        show_elipse: bool = True,
        spinner_delay: float = 80,
        elipse_delay: float = 500,
        spinner_frames: SpinnerSymbols | None = None) -> None:
        '''
        Initializes a Spinner instance.

        Args:
            show_timer (bool): Whether to display a timer showing elapsed time. Defaults to False.
            show_elipse (bool): Whether to display an animated ellipsis after the message. Defaults to True.
            spinner_delay (float): Delay in milliseconds between spinner frames. Defaults to 80.
            elipse_delay (float): Delay in milliseconds between ellipsis frames. Defaults to 500.
            spinner_frames (SpinnerSymbols | None): Custom spinner frames. If None, uses the theme's default spinner frames. Defaults to None.
        '''
            
        self.show_timer: bool = show_timer
        self.show_elipse: bool = show_elipse
        self.spinner_delay: float = spinner_delay
        self.elipse_delay: float = elipse_delay
        self.spinner_frames: SpinnerSymbols | None = spinner_frames

        self.message: str = ''

        self._render_frame: RenderFrame = RenderFrame()
        self._was_cancelled: bool = False
        self._start_time: float = 0
        self._stop_event: Event = Event()
        self._animation_thread: Thread = Thread()

    def start(self, msg: str) -> None:
        '''
        Starts the spinner animation with the provided message.

        Args:
            msg (str): The message to display alongside the spinner.
        '''

        # Terminal state
        self._old_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        if EchoController.is_ctl_echo_enabled():
            EchoController.disable_ctl_echo()

        # Spinner state
        Stdout.put(cc.hide_cursor())
        self._stop_event.clear()
        self._was_cancelled = False
        self._start_time = time.time()
        self.message = msg
        self._animation_thread = Thread(target=self._render_thread)
        self._animation_thread.start()

    def stop(self, msg: str) -> None:
        '''
        Stops the spinner animation and displays a final message.

        Args:
            msg (str): The final message to display after stopping the spinner.
        '''

        if not self._stop_event.is_set():
            self._cleanup()

            theme: Theme = get_active_theme()
            step_marker_submit: str = theme.symbols.step_marker_submit.resolve()
            connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
            prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

            frame_builder: FrameBuilder = FrameBuilder()

            frame_builder.add_line(prefix_muted)

            stop_lines: list[Text] = build_message_header(
                msg,
                theme.text,
                f'{step_marker_submit}  ',
                theme.submit,
                prefix_muted)
            frame_builder.add_lines(*stop_lines)

            frame: tuple[Text, ...] = frame_builder.build()
            self._render_frame.draw_frame(*frame)
        
    def cancel(self, msg: str) -> None:
        '''
        Cancels the spinner animation and displays a cancellation message.

        Args:
            msg (str): The cancellation message to display after stopping the spinner.
        '''

        if not self._stop_event.is_set():
            self._was_cancelled = True
            self._cleanup()

            theme: Theme = get_active_theme()
            step_marker_cancel: str = theme.symbols.step_marker_cancel.resolve()
            connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
            prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

            frame_builder: FrameBuilder = FrameBuilder()

            frame_builder.add_line(prefix_muted)

            cancel_lines: list[Text] = build_message_header(
                msg,
                theme.text,
                f'{step_marker_cancel}  ',
                theme.cancel,
                prefix_muted)
            frame_builder.add_lines(*cancel_lines)

            frame: tuple[Text, ...] = frame_builder.build()
            self._render_frame.draw_frame(*frame)

    def error(self, msg: str) -> None:
        '''
        Displays an error message and stops the spinner animation.

        Args:
            msg (str): The error message to display after stopping the spinner.
        '''

        if not self._stop_event.is_set():
            self._cleanup()

            theme: Theme = get_active_theme()
            step_marker_error: str = theme.symbols.step_marker_error.resolve()
            connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
            prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)

            frame_builder: FrameBuilder = FrameBuilder()

            frame_builder.add_line(prefix_muted)

            error_lines: list[Text] = build_message_header(
                msg,
                theme.text,
                f'{step_marker_error}  ',
                theme.cancel,
                prefix_muted)
            frame_builder.add_lines(*error_lines)

            frame: tuple[Text, ...] = frame_builder.build()
            self._render_frame.draw_frame(*frame)

    def clear(self) -> None:
        '''
        Clears the spinner from the terminal without displaying any message.
        '''

        if not self._stop_event.is_set():
            self._cleanup()
            self._render_frame.clear_frame()

    def is_cancelled(self) -> bool:
        '''
        Returns True if the spinner was cancelled by the user, False otherwise.

        Returns:
            bool: True if the spinner was cancelled, False otherwise.
        '''

        return self._was_cancelled

    def set_message(self, msg: str) -> None:
        '''
        Updates the message displayed alongside the spinner.

        Args:
            msg (str): The new message to display.
        '''

        self.message = msg

    def _handle_interrupt(self, signum, frame):
        '''
        Handles the SIGINT signal (Ctrl+C) to cancel the spinner and raise a CancelException.
        '''

        # Terminal state (just to be safe)
        EchoController.enable_ctl_echo()

        raise CancelException

    def _cleanup(self):
        '''
        Cleans up the spinner by showing the cursor and stopping the animation.
        '''

        self._stop_event.set()

        if self._animation_thread.is_alive():
            self._animation_thread.join()

        # Terminal state
        signal.signal(signal.SIGINT, self._old_sigint_handler)
        EchoController.enable_ctl_echo()
        Stdout.put(cc.show_cursor())

    def _format_time(self, ms: float) -> str:
        '''
        Formats the elapsed time in milliseconds into a human-readable string.

        Args:
            ms (float): The elapsed time in milliseconds.

        Returns:
            str: The formatted time string in the format "Xh Ym Zs", where X, Y, and Z are hours, minutes, and seconds respectively. If hours or minutes are zero, they are omitted from the string.
        '''

        seconds: float = ms // 1000
    
        h: float = seconds // 3600
        seconds %= 3600
    
        m: float = seconds // 60
        s: float = seconds % 60
    
        return f'{f'{int(h)}h ' if h else ''}{f'{int(m)}m ' if m else ''}{int(s)}s'

    def _render_thread(self) -> None:
        '''
        The main rendering loop for the spinner animation. This method runs in a separate thread and updates the spinner's display based on the elapsed time, current spinner frame, ellipsis, and timer.
        '''

        while not self._stop_event.is_set() and not self._was_cancelled:
            time_elapsed_ms: float = (time.time() - self._start_time) * 1000
            
            theme: Theme = get_active_theme()
            connector_bar_vertical: str = theme.symbols.connector_bar_vertical.resolve()
            prefix_muted: Text = Text(f'{connector_bar_vertical}  ', theme.muted)
            prefix_active: Text = Text(f'{connector_bar_vertical}  ', theme.active)
            
            spinner_frames: tuple[str] = theme.symbols.spinner.resolve() if not self.spinner_frames else self.spinner_frames.resolve()
            current_spinner_frame_step: int = int(time_elapsed_ms / self.spinner_delay)
            current_spinner_frame_index: int = current_spinner_frame_step % len(spinner_frames)
            current_spinner_frame: str = spinner_frames[current_spinner_frame_index]
    
            spinner_text: Text = Text(f'{current_spinner_frame}  ', theme.active) + Text(self.message, theme.text)
    
            if self.show_elipse:
                elipse_frames: tuple[str, ...] = tuple(['', '.', '..', '...'])
                current_elipse_frame_step: int = int(time_elapsed_ms / self.elipse_delay)
                current_elipse_frame_index: int = current_elipse_frame_step % len(elipse_frames)
                current_elipse_frame: str = elipse_frames[current_elipse_frame_index]
    
                spinner_text += Text(current_elipse_frame, theme.text)
    
            if self.show_timer:
                formatted_time: str = self._format_time(time_elapsed_ms)
                spinner_text += Text(f' [{formatted_time}]', theme.text)
    
            frame_builder: FrameBuilder = FrameBuilder()

            frame_builder.add_line(prefix_muted)
            
            spinner_text_lines: list[Text] = build_wrapped_lines(spinner_text, prefix_active)
            spinner_text_lines[0].text = spinner_text_lines[0].text[3:]
    
            frame_builder.add_lines(*spinner_text_lines)
            
            frame: tuple[Text, ...] = frame_builder.build()
            self._render_frame.draw_frame(*frame)