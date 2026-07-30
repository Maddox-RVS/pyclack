from pyclack.prompts import ask

def main() -> None:
    value: str = ask(
        message="Enter your name:",
        placeholder="Your name here",
        initial_value=None,
        validate=lambda x: len(x) > 0
    )

if __name__ == '__main__':
    main()