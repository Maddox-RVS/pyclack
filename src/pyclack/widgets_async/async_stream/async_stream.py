from collections.abc import Iterable, AsyncIterable
from ...widgets import stream as sync_stream
import asyncio

async def message(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    '''
    Renders an iterable or asynchronous iterable of strings to the terminal.

    Args:
        iterable (Iterable[str] | AsyncIterable[str]): An iterable or asynchronous iterable of strings to render.
    '''
    
    await asyncio.to_thread(sync_stream.message, iterable)

async def info(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    '''
    Renders an iterable or asynchronous iterable of strings to the terminal, displaying each string as an informational message.

    Args:
        iterable (Iterable[str] | AsyncIterable[str]): An iterable or asynchronous iterable of strings to render as informational messages.
    '''
    
    await asyncio.to_thread(sync_stream.info, iterable)

async def step(iterable: Iterable[str] | AsyncIterable[str]) -> None:
    '''
    Renders an iterable or asynchronous iterable of strings to the terminal, displaying each string as a step message.

    Args:
        iterable (Iterable[str] | AsyncIterable[str]): An iterable or asynchronous iterable of strings to
    '''
    
    await asyncio.to_thread(sync_stream.step, iterable)