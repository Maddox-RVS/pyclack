from ..prompts import (
    ask as sync_ask,
    autocomplete as sync_autocomplete,
    autocomplete_multiselect as sync_autocomplete_multiselect,
    confirm as sync_confirm,
    multiline as sync_multiline,
    multiselect as sync_multiselect,
    password as sync_password,
    pick_date as sync_pick_date,
    select as sync_select,
    select_key as sync_select_key,
    select_path as sync_select_path)
from ..prompts import ClackOption
from ..renderer import Symbol
from typing import Callable
from datetime import date
from pathlib import Path
import asyncio
import os

async def ask(
    message: str, 
    placeholder: str | None, 
    initial_value: str | None, 
    validate: Callable[[str], str | None] | None,
    abort_time: float | None) -> str:
        '''
        Ask the user for input with a message, placeholder, initial value, and validation function.
        Controls are as follows:
        - Use the arrow keys to move the cursor within the input.
        - Press 'Enter' to submit the input.
        - Press 'Backspace' to delete the character before the cursor.
        - Press 'Ctrl+C' or 'esc' to cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            placeholder (str, optional): The placeholder text to display when the input is empty.
            initial_value (str, optional): The initial value of the input.
            validate (Callable[[str], str | None], optional): A function to validate the input.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            str: The user's input.
    
        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_ask,
            message,
            placeholder,
            initial_value,
            validate,
            abort_time)

async def autocomplete(
    message: str,
    options: list[ClackOption], 
    placeholder: str = 'Type to search...',
    show_instructions: bool = True,
    max_items: int = 7,
    filter: Callable[[str, list[ClackOption]], list[ClackOption]] | None = None,
    abort_time: float | None = None) -> ClackOption:
        '''
        Ask the user to select an option from a list of options, with autocomplete functionality.
        
        Controls are as follows:
        - Up/Down arrows to navigate the list of options
        - Backspace to delete the last character in the search input
        - Type to filter the list of options
        - Enter to select the currently highlighted option
        - Press 'Ctrl+C' or 'esc' to cancel the operation
        
        Args:
            message (str): The message to display to the user.
            options (list[ClackOption]): The list of options to display.
            placeholder (str, optional): The placeholder text to display in the search input. Defaults to 'Type to search...'.
            show_instructions (bool, optional): If True, shows the instructions for the prompt. Defaults to True.
            max_items (int, optional): The maximum number of items to display in the list. Defaults to 7.
            filter (Callable[[str, list[ClackOption]], list[ClackOption]] | None, optional): A callable that takes the current search string and the list of options, and returns a filtered list of options. If None, the default filtering behavior is used. Defaults to None.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            ClackOption: The option selected by the user.
    
        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException[ClackOption]: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_autocomplete,
            message,
            options,
            placeholder,
            show_instructions,
            max_items,
            filter,
            abort_time)

async def autocomplete_multiselect(
    message: str,
    options: list[ClackOption], 
    placeholder: str = 'Type to search...',
    show_instructions: bool = True,
    max_items: int = 7,
    filter: Callable[[str, list[ClackOption]], list[ClackOption]] | None = None,
    abort_time: float | None = None) -> list[ClackOption]:
        '''
        Ask the user to select one or more options from a list of options, with autocomplete functionality.
        
        Controls are as follows:
        - Up/Down arrows to navigate the list of options
        - Backspace to delete the last character in the search input
        - Type to filter the list of options
        - Space to select/deselect the currently highlighted option
        - Enter to submit the selected options
        - Press 'Ctrl+C' or 'esc' to cancel the operation
        
        Args:
            message (str): The message to display to the user.
            options (list[ClackOption]): The list of options to display.
            placeholder (str, optional): The placeholder text to display in the search input. Defaults to 'Type to search...'.
            show_instructions (bool, optional): If True, shows the instructions for the prompt. Defaults to True.
            max_items (int, optional): The maximum number of items to display in the list. Defaults to 7.
            filter (Callable[[str, list[ClackOption]], list[ClackOption]] | None, optional): A callable that takes the current search string and the list of options, and returns a filtered list of options. If None, the default filtering behavior is used. Defaults to None.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            list[ClackOption]: The options selected by the user.
    
        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException[list[ClackOption]]: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_autocomplete_multiselect,
            message,
            options,
            placeholder,
            show_instructions,
            max_items,
            filter,
            abort_time)

async def confirm(
    message: str,
    active: str = 'Yes',
    inactive: str = 'No',
    vertical: bool = False,
    default_option: bool = True,
    abort_time: float | None = None) -> bool:
        '''
        Prompt the user for a yes/no confirmation. Controls are as follows:
        - Use the arrow keys (or h/j/k/l) to toggle between 'Yes' and 'No'.
        - Press 'Enter' to submit the selection.
        - Press 'Ctrl+C' or 'esc' to cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            active (str): The text to display for the active (true) option.
            inactive (str): The text to display for the inactive (false) option.
            default_option (bool): The default option for the confirmation.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            bool: The user's confirmation.
    
        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_confirm,
            message,
            active,
            inactive,
            vertical,
            default_option,
            abort_time)

async def multiline(
    message: str, 
    placeholder: str | None = None, 
    initial_value: str | None = None, 
    validate: Callable[[str], str | None] | None = None,
    show_submit: bool = False,
    abort_time: float | None = None) -> str:
        '''
        Ask the user for input with a message, placeholder, initial value, and validation function.
        Controls are as follows:
        - Use the arrow keys to move the cursor within the input.
        - Press 'Enter' to go down a line.
        - Press 'Tab' to toggle focus on the submit button (if shown)
        - Press 'Enter' on submit button to submit (if shown), else press 'Enter' twice to submit.
        - Press 'Backspace' to delete the character before the cursor.
        - Press 'Ctrl+C' or 'esc' to cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            placeholder (str, optional): The placeholder text to display when the input is empty.
            initial_value (str, optional): The initial value of the input.
            validate (Callable[[str], str | None], optional): A function to validate the input.
            show_submit (bool, optional): When True it shows a ` [ submit ] ` button that can be focused with 'Tab', when False no submit button is shown and pressing 'Enter' twice will submit. 
            Defaults to False.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            str: The user's input.
    
        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_multiline,
            message,
            placeholder,
            initial_value,
            validate,
            show_submit,
            abort_time)

async def multiselect(
    message: str,
    options: list[ClackOption], 
    show_instructions: bool = True,
    max_items: int = 7,
    abort_time: float | None = None) -> list[ClackOption]:
        '''
        Ask the user to select multiple options from a list of options.
    
        Controls are as follows:
        - Up/Down arrows or k/j to navigate the options.
        - Space to select/deselect an option.
        - Enter to submit the selected options.
        - Press 'Ctrl+C' or 'esc' to cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            options (list[ClackOption]): The list of options to display to the user.
            show_instructions (bool, optional): Whether to show instructions for the user. Defaults to True.
            max_items (int, optional): The maximum number of items to display at once. Defaults to 7.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            list[ClackOption]: The list of selected options.
    
        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_multiselect,
            message,
            options,
            show_instructions,
            max_items,
            abort_time)
        
async def password(
    message: str, 
    mask: Symbol | None = None,
    show_nothing: bool = False,
    clear_on_error: bool = False,
    validate: Callable[[str], str | None] | None = None,
    abort_time: float | None = None) -> str:
        '''
        Ask the user for input as a password.
        Controls are as follows:
        - Backspace: Delete the last character in the input buffer.
        - Enter: Submit the input as the password.
        - Ctrl+C or esc: Cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            mask (Symbol, optional): The symbol to use for masking the input. Defaults to None
            show_nothing (bool, optional): If True, the input will not be displayed at all. Defaults to False.
            clear_on_error (bool, optional): If True, the input buffer will be cleared on error. Defaults to False.
            validate (Callable[[str], str | None], optional): A function to validate the input. Defaults to None.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            str: The user's input as a password.
    
        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_password,
            message,
            mask,
            show_nothing,
            clear_on_error,
            validate,
            abort_time)

async def pick_date(
    message: str,
    initial_date: date,
    min_date: date,
    max_date: date,
    validate: Callable[[date], str | None] | None = None,
    abort_time: float | None = None) -> date:
        '''
        Ask the user to select a date within a specified range.
        Controls are as follows:
        - Use the arrow keys or 'h', 'j', 'k', 'l' to navigate between the month, day, and year fields.
        - Use the up and down arrow keys or 'j' and 'k' to increase or decrease the value of the selected field.
        - Type numbers to input values directly into the selected field.
        - Press 'Enter' to submit the selected date.
        - Press 'Tab' to move to the next field.
        - Press 'Backspace' to clear the selected field or move to the previous field if it is already empty.
        - Press 'Ctrl+C' or 'esc' to cancel the prompt.
    
        Args:
            message (str): The message to display to the user.
            initial_date (date): The initial date to display in the prompt.
            min_date (date): The minimum date that can be selected.
            max_date (date): The maximum date that can be selected.
            validate (Callable[[date], str | None], optional): A function that takes a date and returns an error message if the date is invalid, or None if the date is valid.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            date: The date selected by the user.
    
        Raises:
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_pick_date,
            message,
            initial_date,
            min_date,
            max_date,
            validate,
            abort_time)

async def select(
    message: str,
    options: list[ClackOption], 
    show_instructions: bool = True,
    max_items: int = 7,
    abort_time: float | None = None) -> ClackOption:
        '''
        Ask the user to select one option from a list of options.
    
        Controls are as follows:
        - Up/Down arrows or k/j to navigate the options.
        - Enter to submit the selected option.
        - Press 'Ctrl+C' or 'esc' to cancel the operation.
    
        Args:
            message (str): The message to display to the user.
            options (list[ClackOption]): The list of options to choose from.
            show_instructions (bool, optional): If True, show instructions. Defaults to True.
            max_items (int, optional): The maximum number of items to display. Defaults to 7.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
    
        Returns:
            ClackOption: The selected option.
    
        Raises:
            RuntimeError: If the options list is empty or if all options are disabled.
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_select,
            message,
            options,
            show_instructions,
            max_items,
            abort_time)

async def select_key(
    message: str,
    options: list[ClackOption[str]],
    case_sensitive: bool = True,
    abort_time: float | None = None) -> ClackOption[str]:
        '''
        Prompt the user to select an option by pressing a key.
    
        Controls are as follows:
        - Press the key corresponding to the desired option to select it.
        - Press 'Enter' to select the first option.
        - Press 'Ctrl+C' or 'esc' to cancel the prompt.
    
        Args:
            message (str): The message to display to the user.
            options (list[ClackOption[str]]): A list of ClackOption objects representing the available options. 
            case_sensitive (bool): Whether the key selection should be case-sensitive.
            abort_time (float | None): The time after which the prompt should be aborted, or None if no timeout is set.
    
        Returns:
            ClackOption[str]: The selected option.
    
        Raises:
            RuntimeError: If the options list is empty, all options are disabled, duplicate option values are present, option value is not a valid key, or option value is not of type str.
            CancelException: If the prompt is cancelled by the user.
        '''
        
        return await asyncio.to_thread(
            sync_select_key,
            message,
            options,
            case_sensitive,
            abort_time)

async def select_path(
    message: str,
    placeholder: str = 'Type to search...',
    show_instructions: bool = True,
    max_items: int = 7,
    root: Path = Path(os.getcwd()),
    directory: bool = False,
    abort_time: float | None = None) -> Path:
        '''
        Ask the user to select an option from a list of options, with autocomplete functionality.
        
        Controls are as follows:
        - Up/Down arrows to navigate the list of options
        - Backspace to delete the last character in the search input
        - Type to filter the list of options
        - Enter to select the currently highlighted option
        - Press 'Ctrl+C' or 'esc' to cancel the operation
        
        Args:
            message (str): The message to display to the user.
            placeholder (str, optional): The placeholder text to display in the search input. Defaults to 'Type to search...'.
            show_instructions (bool, optional): If True, shows the instructions for the prompt. Defaults to True.
            max_items (int, optional): The maximum number of items to display in the list. Defaults to 7.
            root (Path, optional): The root directory to start the search from. Defaults to the current working directory.
            directory (bool, optional): If True, only directories will be shown in the list of options. If False, both files and directories will be shown. Defaults to False.
            abort_time (float, optional): Floating point number representing seconds in time before the prompt is auto-cancelled, if set to None the prompt will never auto-cancel. Defaults to None.
            
        Returns:
             Path: The selected path.
             
        Raises:
            FileNotFoundError: If the root path does not exist.
            CancelException: If the user cancels the operation.
        '''
        
        return await asyncio.to_thread(
            sync_select_path,
            message,
            placeholder,
            show_instructions,
            max_items,
            root,
            directory,
            abort_time)