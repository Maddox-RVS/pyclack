from ...widgets import log as sync_log
import asyncio

class Log:
    '''
    A static class that provides methods to display various types of log messages in a structured format,
    including standard messages, informational messages, warnings, errors, and success notifications.
    '''

    @staticmethod
    async def message(msg: str) -> None:
        '''
        Displays a standard message.

        Args:
            msg (str): The message to display.
        '''

        await asyncio.to_thread(sync_log.message, msg)

    @staticmethod
    async def info(msg: str) -> None:
        '''
        Displays an informational message.

        Args:
            msg (str): The informational message to display.
        '''
        
        await asyncio.to_thread(sync_log.info, msg)

    @staticmethod
    async def warning(msg: str) -> None:
        '''
        Displays a warning message.

        Args:
            msg (str): The warning message to display.
        '''

        await asyncio.to_thread(sync_log.warning, msg)

    @staticmethod
    async def warn(msg: str) -> None:
        '''
        Displays a warning message. This is an alias for the `warning` method.

        Args:
            msg (str): The warning message to display.
        '''
        
        await asyncio.to_thread(sync_log.warn, msg)

    @staticmethod
    async def error(msg: str) -> None:
        '''
        Displays an error message.

        Args:
            msg (str): The error message to display.
        '''
        
        await asyncio.to_thread(sync_log.error, msg)

    @staticmethod
    async def success(msg: str) -> None:
        '''
        Displays a success message.

        Args:
            msg (str): The success message to display.
        '''
        
        await asyncio.to_thread(sync_log.success, msg)

    @staticmethod
    async def step(msg: str) -> None:
        '''
        Displays a step message, typically used to indicate progress in a multi-step process.

        Args:
            msg (str): The step message to display.
        '''
        
        await asyncio.to_thread(sync_log.step, msg)