from pyclack.prompts import ask, autocomplete, autocomplete_multiselect, confirm, multiline, multiselect, password, pick_date, select, select_key, select_path, ClackOption, CancelException
from pyclack.widgets import intro, outro, cancel, note, TaskLog, log, box, Spinner, Activity, stream, Progress
from collections.abc import AsyncIterable
from pyclack import set_active_theme
from pyclack.renderer import Style
from typing import LiteralString
from pyclack import Themes
from datetime import date
from pathlib import Path
from typing import cast
import subprocess
import time

def main() -> None:
    # set_active_theme(Themes.AUTUMN)
    # set_active_theme(Themes.ARCTIC)
    # set_active_theme(Themes.CORAL)
    # set_active_theme(Themes.CRIMSON)
    # set_active_theme(Themes.CYBERPUNK)
    # set_active_theme(Themes.DARK)
    # set_active_theme(Themes.DESERT)
    # set_active_theme(Themes.FOCUS)
    # set_active_theme(Themes.FOREST)
    # set_active_theme(Themes.FROST)
    # set_active_theme(Themes.GALAXY)
    # set_active_theme(Themes.GOLD)
    # set_active_theme(Themes.HIGH_CONTRAST)
    # set_active_theme(Themes.LIGHT)
    # set_active_theme(Themes.MATRIX)
    # set_active_theme(Themes.MIDNIGHT)
    # set_active_theme(Themes.MINT)
    # set_active_theme(Themes.MONOCHROME)
    # set_active_theme(Themes.NEBULA)
    # set_active_theme(Themes.OCEAN)
    # set_active_theme(Themes.PASTEL)
    # set_active_theme(Themes.RETRO)
    # set_active_theme(Themes.ROYAL)
    # set_active_theme(Themes.SAKURA)
    # set_active_theme(Themes.SEPIA)
    # set_active_theme(Themes.STEEL)
    # set_active_theme(Themes.SUNSET)
    # set_active_theme(Themes.TERRA)
    # set_active_theme(Themes.TWILIGHT)
    # set_active_theme(Themes.VOLCANO)
    
    intro('Welcome to the demo', Style(bg_color='blue'))

    try:
        def validate_name(name: str) -> str | None:
            if not name.strip(): return 'Value is required'
        
        name: str = ask(
            message="What's your name?",
            placeholder='(e.g. Bobby)',
            validate=validate_name)
    except CancelException as e:
        e = cast(CancelException[str], e)
        cancel(f'You cancelled the ask prompt with "{e.value}" filled in!')
        exit(0)

    try:
        drink_options: list[ClackOption[str]] = [
            ClackOption('water', 'Water', 'ice cold'),
            ClackOption('lemondade', 'Lemonade', 'sweet'),
            ClackOption('gatorade', 'Gatorade', 'out of stock', disabled=True),
            ClackOption('coffee', 'Coffee', 'scolding hot'),
            ClackOption('redbull', 'Redbull', 'out of stock', disabled=True),
            ClackOption('iced tea', 'Iced Tea', 'ice cold'),
            ClackOption('tea', 'Tea', 'scolding hot')]

        drink_choice: ClackOption[str] = autocomplete(
            message='Please choose a drink:',
            options=drink_options)
    except CancelException:
        cancel('You cancelled the autocomplete prompt!')
        exit(0)

    try:
        animal_options: list[ClackOption[str]] = [
            ClackOption('monkey', 'Monkey', 'ooo ooo AAH AAH'),
            ClackOption('snake', 'Snake', 'sssssSSSSS'),
            ClackOption('bird', 'Bird', 'chirp chirp'),
            ClackOption('trex', 'T-Rex', 'extinct', disabled=True),
            ClackOption('cat', 'Cat', 'meow'),
            ClackOption('dog', 'Dog', 'woof woof'),
            ClackOption('wooly mamoth', 'Wooly Mammoth', 'extinct', disabled=True),
            ClackOption('dolphin', 'Dolphin', 'click click')]

        animal_choices: list[ClackOption[str]] = autocomplete_multiselect(
            message='Please select all the animals that interest you!',
            options=animal_options)
    except CancelException:
        cancel('You cancelled the autocomplete multiselect prompt!')
        exit(0)

    try:
        would_go_skydiving: bool = confirm(
            message='Would you ever go skydiving?',
            active='Hell yes',
            inactive='Absolutely not')

        would_go_scubadiving: bool = confirm(
            message='Would you ever go scubadiving?',
            active='Yeah sounds cool',
            inactive='Nope too scary',
            vertical=True)
    except CancelException:
        cancel('You cancelled the confirm prompt!')
        exit(0)

    try:
        def validate_bio(bio: str) -> str | None:
            if not bio.strip(): return 'Value is required!'
        
        bio: str = multiline(
            message='Anything you want to share?',
            placeholder='Tell us about yourself...',
            validate=validate_bio,
            show_submit=True)
    except CancelException:
        cancel('You cancelled the multiline prompt!')
        exit(0)

    try:
        menu_options: list[ClackOption[str]] = [
            ClackOption('pizza', 'Pizza', 'cheesy goodness'),
            ClackOption('burger', 'Burger', 'juicy and delicious'),
            ClackOption('salad', 'Salad', 'coming soon', disabled=True),
            ClackOption('sushi', 'Sushi', 'raw fish and rice'),
            ClackOption('tacos', 'Tacos', 'spicy and flavorful')]

        menu_choices: list[ClackOption[str]] = multiselect(
            message='Please choose from the following items on our menu:',
            options=menu_options)
    except CancelException:
        cancel('You cancelled the multiselect prompt!')
        exit(0)

    try:
        def validate_pass(user_pass: str) -> str | None:
            if not user_pass: return 'Value is required!'
            elif len(user_pass) < 8: return 'Password must be longer than 8 characters!'
        
        user_pass: str = password(message='Create a password:', validate=validate_pass)
    except CancelException:
        cancel('You cancelled the password prompt!')
        exit(0)

    try:
        birthday: date = pick_date(
            message='Please enter you birthday:',
            initial_date=date.today(),
            min_date=date(1990, 1, 1),
            max_date=date.today())
    except CancelException:
        cancel('You cancelled the pick date prompt!')
        exit(0)

    try:
        color_options: list[ClackOption[str]] = [
            ClackOption('red', 'Red', 'the color of fire'),
            ClackOption('green', 'Green', 'the color of grass'),
            ClackOption('blue', 'Blue', 'the color of the sky'),
            ClackOption('yellow', 'Yellow', 'the color of the sun'),
            ClackOption('purple', 'Purple', 'the color of royalty'),
            ClackOption('orange', 'Orange', 'the color of oranges'),
            ClackOption('pink', 'Pink', 'the color of love'),
            ClackOption('black', 'Black', 'the color of darkness'),
            ClackOption('white', 'White', 'the color of purity')]

        favorite_color: ClackOption[str] = select(
            message='Please select your favorite color:',
            options=color_options)
    except CancelException:
        cancel('You cancelled the select prompt!')
        exit(0)

    try:
        key_choices: list[ClackOption[str]] = [
            ClackOption('y', 'Continue'),
            ClackOption('n', 'Stop'),
            ClackOption('t', 'Try again', 'disabled', disabled=True),
            ClackOption('s', 'Skip', 'optional')]
        
        key_choice: ClackOption[str] = select_key(
            'Please chose one of the following options:',
            options=key_choices,
            case_sensitive=False)
    except CancelException:
        cancel('You cancelled the select key prompt!')
        exit(0)

    try:
        path_choice: Path = select_path(message='Please select a file or directory:')
    except CancelException:
        cancel('You cancelled the select path prompt!')
        exit(0)

    task_log: TaskLog = TaskLog(title='Compiling units', limit=5, retain_log=True)
    try:
        for i in range(20):
            task_log.message(f'Compiling unit {i + 1}...')
            time.sleep(0.1)
    except CancelException:
        cancel('You cancelled the TaskLog prompt!')
        exit(0)
    task_log.success('Compilation complete')

    spinner: Spinner = Spinner()
    try:
        spinner.start('Loading final results')
        time.sleep(5)
    except CancelException:
        spinner.cancel('Final results cancelled')
        cancel('You have cancelled the spinner widget!')
        exit(0)
    spinner.stop('Final results loaded')

    finale_message: str = (
        f'Name: {name}\n'
        f'Drink: {drink_choice.label}\n'
        f'Animals: {", ".join([a.label for a in animal_choices])}\n'
        f'Skydiving: {"Yes" if would_go_skydiving else "No"}\n'
        f'Scubadiving: {"Yes" if would_go_scubadiving else "No"}\n'
        f'Bio: {bio}\n'
        f'Menu: {", ".join([m.label for m in menu_choices])}\n'
        f'Password: {user_pass}\n'
        f'Birthday: {birthday}\n'
        f'Favorite Color: {favorite_color.label}\n'
        f'Key Choice: {key_choice.label}\n'
        f'Path Choice: {path_choice}')

    note('Final Results', finale_message)

    time.sleep(2)

    log.message('You can log messages!')
    log.info('You can log info!')
    log.warn('You can log warnings using an alias!')
    log.warning('You can log warnings!')
    log.error('You can log errors!')
    log.success('You can log success!')
    log.step('You can log steps!')

    box('This is the content of the box', 'Box Title')

    progress: Progress = Progress(max=1500, size=40)
    progress.start('Downloading dependencies')
    try:
        for i in range(1500):
            time.sleep(0.005)
            if i == 500: progress.set_message('Unpacking dependencies')
            if i == 1000: progress.set_message('Installing dependencies')
            progress.advance()
    except CancelException:
        progress.cancel('Download cancelled')
        cancel('You cancelled the progress widget!')
        exit(0)
    progress.stop('Done!')

    example_text: str = (
        'Hello, this text is being streamed from an AsyncIterable!\n'
        'Each word has exactly an 0.1 second delay before being printed!\n'
        'Here\'s the code:\n\n'
        'async def generated_asyc_iterable() -> AsyncIterable[str]:\n'
        '    for item in sync_iterable:\n'
        '        time.sleep(0.1)\n'
        '        yield item')

    sync_iterable: list[LiteralString] = example_text.split(' ')
    sync_iterable = [item + ' ' for item in sync_iterable]

    async def generated_asyc_iterable() -> AsyncIterable[str]:
        for item in sync_iterable:
            time.sleep(0.1)
            yield item

    async_iterable: AsyncIterable[str] = generated_asyc_iterable()

    try:
        stream.message(async_iterable)

        stream.info(open('demos/banner.txt', encoding='utf-8'))

        stream.step(['streams have steps too!', ' Alright...', ' Goodbye!'])
    except CancelException:
        cancel('You cancelled the stream prompt!')
        exit(0)

    activity: Activity = Activity(limit=8, show_timer=True, show_elipse=True)
    activity.start('Displaying subprocess running Python code below')
    try:
        process = subprocess.Popen(
            [
                "python",
                "-c",
                "import time; [print(f'Output line {i}', flush=True) or time.sleep(0.02) for i in range(200)]",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        count: int = 0
        for line in process.stdout:
            count += 1
            if count == 100: activity.set_spinner_message('Python subprocess is counting to 200')
            activity.set_activity_message(activity.get_activity_message() + line)
    except CancelException:
        activity.cancel('Activity cancelled')
        cancel('You cancelled the activity widget!')
        exit(0)
    activity.stop('Finished display!')

    outro('Thanks for interacting with the demo!')

if __name__ == '__main__':
    main()