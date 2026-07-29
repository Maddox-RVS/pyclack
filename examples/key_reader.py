from pyclack.terminal import KeyReader

def main() -> None:
    while True:
        key: str = KeyReader.readkey()
        print(f'You pressed: {key}')
        if key == 'CTRL_C':
            print('Exiting...')
            break

if __name__ == "__main__":
    main()