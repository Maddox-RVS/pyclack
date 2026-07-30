from pyclack.prompts import ask, intro, outro, CancelException
from pyclack.config import set_print_mode_ascii
from typing import Optional

def main() -> None:
    intro('Welcome to the Ask Example')

    try:
        def validate_name(value: str) -> Optional[str]:
            if len(value) == 0: return 'Value is required!'

        name: str = ask(
            message='Enter your name:',
            placeholder='Your name here',
            initial_value='Bob',
            validate=validate_name,
            cancellation_message='You cancelled the name input!'
        )
    except CancelException: exit(0)

    try:
        def validate_age(value: str) -> Optional[str]:
            try: int(value)
            except: return 'Value must be a number!'

        age: int = int(ask(
            message='Enter your age:',
            placeholder='Your age here',
            initial_value='21',
            validate=validate_age,
            cancellation_message='You cancelled the age input!'
        ))
    except CancelException: exit(0)

    try:
        def validate_fav_food(value: str) -> str:
            if len(value) == 0: return 'Value is required!'

        favorite_food: str = ask(
            message='Whats your favorite food?',
            placeholder='Your favorite food here',
            validate=validate_fav_food,
            cancellation_message='You cancelled the favorite food input!',
        )
    except CancelException as e:
        print(f'\nYou cancelled with "{e.value}" entered!')
        exit(0)

    outro(f'Glad to know that your favorite food is {favorite_food} and that you are {age} years old! Goodbye, {name}! 👋')

if __name__ == '__main__':
    main()