import sys

class Stdout:
    @staticmethod
    def write(text: str) -> None:
        '''
        Write text to stdout without adding a newline. This is a thin wrapper around sys.stdout.write.
        '''

        sys.stdout.write(text)

    @staticmethod
    def flush() -> None:
        '''
        Flush the stdout buffer. This is a thin wrapper around sys.stdout.flush.
        '''

        sys.stdout.flush()

    @staticmethod
    def put(text: str) -> None:
        '''
        Convenience method to write text to stdout and flush immediately.
        '''

        Stdout.write(text)
        Stdout.flush()