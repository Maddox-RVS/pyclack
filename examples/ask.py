from pyclack.prompts import ask, intro, outro

def main() -> None:
    intro('Welcome to the Ask Example')

    value: str = ask(
        message="Enter your name:",
        placeholder="Your name here",
        initial_value=None,
        validate=lambda x: len(x) > 0
    )

    outro(f'Goodbye, {value}! 👋')

if __name__ == '__main__':
    main()