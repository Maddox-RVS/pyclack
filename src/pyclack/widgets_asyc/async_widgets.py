from ..widgets import (
    Activity as SyncActivity,
    box as sync_box,
    cancel as sync_cancel,
    intro as sync_intro,
    note as sync_note,
    outro as sync_outro,
    Progress as SyncProgress,
    Spinner as SyncSpinner,
    TaskLog as SyncTaskLog)
from ..renderer import Symbol, SpinnerSymbols, Style
from ..widgets import ProgressStyle
from ..prompts import Alignment
import asyncio

class Activity():
    '''
    A class that manages and displays an activity spinner in the terminal, with support for messages, timers, and cancellation.
    '''
    
    def __init__(self, 
        limit: int | None = None, 
        show_timer: bool = False, 
        show_elipse: bool = True, 
        spinner_delay: float = 80, 
        elipse_delay: float = 500, 
        spinner_frames: SpinnerSymbols | None = None) -> None:
        '''
        Initializes a Activity instance.

        Args:
            limit (int | None): The maximum number of activity messages to display. If None, no limit is applied. Defaults to None.
            show_timer (bool): Whether to display a timer showing the elapsed time since the spinner started. Defaults to False.
            show_elipse (bool): Whether to display an ellipsis animation after the spinner message. Defaults to True.
            spinner_delay (float): The delay in milliseconds between spinner frames. Defaults to 80.
            elipse_delay (float): The delay in milliseconds between ellipsis frames. Defaults to 500.
            spinner_frames (SpinnerSymbols | None): Custom spinner frames to use for the spinner animation.
        '''
            
        self.activity: SyncActivity = SyncActivity(limit, show_timer, show_elipse, spinner_delay, elipse_delay, spinner_frames)

    async def start(self, msg: str) -> None:
        '''
        Starts the activity animation with the provided message.

        Args:
            msg (str): The message to display alongside the spinner.
        '''
        
        await asyncio.to_thread(
            self.activity.start,
            msg)

    async def stop(self, msg: str) -> None:
        '''
        Stops the activity animation and displays a final message.

        Args:
            msg (str): The final message to display after stopping the activity.
        '''
        
        await asyncio.to_thread(
            self.activity.stop,
            msg)

    async def cancel(self, msg: str) -> None:
        '''
        Cancels the activity animation and displays a cancellation message.

        Args:
            msg (str): The cancellation message to display after stopping the activity.
        '''
        
        await asyncio.to_thread(
            self.activity.cancel,
            msg)

    async def error(self, msg: str) -> None:
        '''
        Displays an error message and stops the activity animation.

        Args:
            msg (str): The error message to display after stopping the activity.
        '''
        
        await asyncio.to_thread(
            self.activity.error,
            msg)

    async def clear(self) -> None:
        '''
        Clears the activity from the terminal without displaying any message.
        '''
        
        await asyncio.to_thread(self.activity.clear)

    async def is_cancelled(self) -> bool:
        '''
        Returns True if the activity was cancelled by the user, False otherwise.

        Returns:
            bool: True if the activity was cancelled, False otherwise.
        '''
        
        return await asyncio.to_thread(self.activity.is_cancelled)

    async def set_spinner_message(self, msg: str) -> None:
        '''
        Updates the message displayed alongside the spinner.

        Args:
            msg (str): The new message to display.
        '''
        
        await asyncio.to_thread(
            self.activity.set_spinner_message,
            msg)

    async def set_activity_message(self, msg: str) -> None:
        '''
        Updates the message displayed for the activity.

        Args:
            msg (str): The new message to display.
        '''
        
        await asyncio.to_thread(
            self.activity.set_activity_message,
            msg)

    async def get_activity_message(self) -> str:
        '''
        Returns the current message displayed for the activity.

        Returns:
            str: The current activity message.
        '''
        
        return await asyncio.to_thread(self.activity.get_activity_message)

async def box(
    content: str,
    title: str = '',
    content_align: Alignment = Alignment.LEFT,
    title_align: Alignment = Alignment.LEFT,
    width: int | None = None,
    rounded: bool = True,
    title_padding: int = 0,
    content_padding: int = 2) -> None:
    '''
    Displays a customizable, fully-bordered box around text content, with an optional embedded title.

    Args:
        content (str): The text content shown inside the box.
        title (str): The title text embedded in the top border. Defaults to '' (no title).
        content_align (Alignment): Horizontal alignment of the content within the box. Defaults to Alignment.LEFT.
        title_align (Alignment): Horizontal alignment of the title within the top border. Defaults to Alignment.LEFT.
        width (int | None): Fixed total box width, or None to auto-fit the content/title up to the terminal's width. Defaults to None.
        rounded (bool): Use rounded corners when True, square corners when False. Defaults to True.
        title_padding (int): Number of spaces surrounding the title text. Defaults to 1.
        content_padding (int): Number of spaces surrounding content lines, on each side. Defaults to 2.
    '''

    await asyncio.to_thread(
        sync_box,
        content,
        title,
        content_align,
        title_align,
        width,
        rounded,
        title_padding,
        content_padding)

async def cancel(message: str) -> None:
    '''
    Display a cancellation message to the user.

    Args:
        message (str): The cancellation message to display.
    '''

    await asyncio.to_thread(
        sync_cancel,
        message)

async def intro(title: str, custom_style: Style | None = None) -> None:
    '''
    Display an introductory message with a title.

    Args:
        title (str): The title to display to the user.
        custom_style (Style | None, optional): The custom style to use for the intro.
    '''

    await asyncio.to_thread(
        sync_intro,
        title,
        custom_style)

async def note(title: str, message: str) -> None:
    '''
    Displays a note to the user with a title and message.

    Args:
        title (str): The title of the note.
        message (str): The message content of the note.
    '''

    await asyncio.to_thread(
        sync_note,
        title,
        message)

async def outro(message: str, custom_style: Style | None = None) -> None:
    '''
    Display an exit message.

    Args:
        message (str): The message to display to the user.
        custom_style (Style | None, optional): The custom style to use for the outro.
    '''

    await asyncio.to_thread(
        sync_outro,
        message,
        custom_style)

class Progress():
    '''
    A customizable progress widget that displays a progress bar, spinner, and optional timer in the terminal. It supports different styles, message updates, and cancellation handling.
    '''
    
    def __init__(self, 
        max: int, 
        size: int, 
        style: ProgressStyle = ProgressStyle.HEAVY, 
        show_timer: bool = False, 
        show_elipse: bool = True, 
        spinner_delay: float = 80, 
        elipse_delay: float = 500, 
        spinner_frames: SpinnerSymbols | None = None):
        '''
        Initializes a new instance of the Progress widget.

        Args:
            max (int): The maximum value of the progress bar.
            size (int): The total number of characters used to represent the progress bar.
            style (ProgressStyle): The style of the progress bar. Defaults to ProgressStyle.HEAVY.
            show_timer (bool): Whether to display a timer showing elapsed time. Defaults to False.
            show_elipse (bool): Whether to display an ellipsis animation. Defaults to True.
            spinner_delay (float): The delay in milliseconds between spinner frames. Defaults to 80.
            elipse_delay (float): The delay in milliseconds between ellipsis frames. Defaults to 500.
            spinner_frames (SpinnerSymbols | None): Custom spinner frames to use. If None, the default spinner frames from the active theme will be used. Defaults to None.
        '''
            
        self.progress: SyncProgress = SyncProgress(max, size, style, show_timer, show_elipse, spinner_delay, elipse_delay, spinner_frames)

    async def advance(self, amount: int = 1) -> None:
        '''
        Advances the progress bar by the specified amount, up to the maximum value.

        Args:
            amount (int): The amount to advance the progress bar by. Defaults to 1.
        '''
        
        await asyncio.to_thread(
            self.progress.advance,
            amount)

    async def start(self, msg: str) -> None:
        '''
        Starts the progress animation with the provided message.

        Args:
            msg (str): The message to display alongside the progress bar.
        '''
        
        await asyncio.to_thread(
            self.progress.start,
            msg)

    async def stop(self, msg: str) -> None:
        '''
        Stops the progress animation and displays a final message.

        Args:
            msg (str): The final message to display after stopping the progress bar.
        '''
        
        await asyncio.to_thread(
            self.progress.stop,
            msg)

    async def cancel(self, msg: str) -> None:
        '''
        Cancels the progress animation and displays a cancellation message.

        Args:
            msg (str): The cancellation message to display after stopping the progress bar.
        '''
        
        await asyncio.to_thread(
            self.progress.cancel,
            msg)

    async def error(self, msg: str) -> None:
        '''
        Displays an error message and stops the progress animation.

        Args:
            msg (str): The error message to display after stopping the progress bar.
        '''
        
        await asyncio.to_thread(
            self.progress.error,
            msg)

    async def clear(self) -> None:
        '''
        Clears the progress bar from the terminal without displaying any message.
        '''
        
        await asyncio.to_thread(self.progress.clear)

    async def is_cancelled(self) -> bool:
        '''
        Returns True if the progress bar was cancelled by the user, False otherwise.

        Returns:
            bool: True if the progress bar was cancelled, False otherwise.
        '''
        
        return await asyncio.to_thread(self.progress.is_cancelled)

    async def set_message(self, msg: str) -> None:
        '''
        Updates the message displayed alongside the spinner.

        Args:
            msg (str): The new message to display.
        '''
        
        await asyncio.to_thread(
            self.progress.set_message,
            msg)

class Spinner():
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
        
        self.spinner: SyncSpinner = SyncSpinner(show_timer, show_elipse, spinner_delay, elipse_delay, spinner_frames)

    async def start(self, msg: str) -> None:
        '''
        Starts the spinner animation with the provided message.

        Args:
            msg (str): The message to display alongside the spinner.
        '''
        
        await asyncio.to_thread(
            self.spinner.start,
            msg)

    async def stop(self, msg: str) -> None:
        '''
        Stops the spinner animation and displays a final message.

        Args:
            msg (str): The final message to display after stopping the spinner.
        '''
        
        await asyncio.to_thread(
            self.spinner.stop,
            msg)

    async def cancel(self, msg: str) -> None:
        '''
        Cancels the spinner animation and displays a cancellation message.

        Args:
            msg (str): The cancellation message to display after stopping the spinner.
        '''
        
        await asyncio.to_thread(
            self.spinner.cancel,
            msg)

    async def error(self, msg: str) -> None:
        '''
        Displays an error message and stops the spinner animation.

        Args:
            msg (str): The error message to display after stopping the spinner.
        '''
        
        await asyncio.to_thread(
            self.spinner.error,
            msg)

    async def clear(self) -> None:
        '''
        Clears the spinner from the terminal without displaying any message.
        '''
        
        await asyncio.to_thread(self.spinner.clear)

    async def is_cancelled(self) -> bool:
        '''
        Returns True if the spinner was cancelled by the user, False otherwise.

        Returns:
            bool: True if the spinner was cancelled, False otherwise.
        '''
        
        return await asyncio.to_thread(self.spinner.is_cancelled)

    async def set_message(self, msg: str) -> None:
        '''
        Updates the message displayed alongside the spinner.

        Args:
            msg (str): The new message to display.
        '''
        
        await asyncio.to_thread(
            self.spinner.set_message,
            msg)

class TaskLog():
    '''
    A class that manages and displays a log of messages in a structured format, with support for titles, 
    message limits, and success states.
    '''
    
    def __init__(self, 
        title: str, 
        limit: int | None = None, 
        retain_log: bool = False) -> None:
        '''
        Initializes a TaskLog instance.

        Args:
            title (str): The title of the task log.
            limit (int | None): The maximum number of messages to keep in the log. If None, no limit is applied. Defaults to None.
            retain_log (bool): Whether to retain the log history instead of clearing it to limit if one is set. Defaults to False.
        '''
            
        self.tast_log: SyncTaskLog = SyncTaskLog(title, limit, retain_log)

    async def get_log(self) -> list[str]:
        '''
        Returns the current log of messages.

        Returns:
            list[str]: The list of messages in the log.
        '''
        
        return await asyncio.to_thread(self.tast_log.get_log)

    async def message(self, msg: str) -> None:
        '''
        Adds a message to the log.

        Args:
            msg (str): The message to add to the log.
        '''
        
        await asyncio.to_thread(
            self.tast_log.message,
            msg)

    async def success(self, msg: str) -> None:
        '''
        Marks the task as successful, adds a success message to the log, and renders it.

        Args:
            msg (str): The success message to add to the log.
        '''
        
        await asyncio.to_thread(
            self.tast_log.success,
            msg)