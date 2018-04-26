import inspect
import sys
from collections import namedtuple
from typing import Callable, MutableMapping, Tuple, Iterator, ClassVar, Optional, Any, IO

python_print: Callable[[Tuple[Any, ...], str, str, Optional[IO[str]], bool], None] = print


class Script(object):
    BASE_COMMAND: ClassVar[str] = f'python3 {__file__}'
    CommandProperties: ClassVar[namedtuple] = namedtuple('CommandProperties', ('args', 'callable'))

    def __init__(self, *commands: Callable[..., None]):

        # noinspection PyCallByClass
        self.commands: MutableMapping[str, Script.CommandProperties] = {
            command.__name__: Script.CommandProperties(
                tuple(inspect.signature(command).parameters.keys()),
                command
            ) for command in commands
        }

    def usage(self) -> None:
        python_print()

        python_print('Usage:')
        for name, properties in self.commands.items():
            python_print('\t' + ' '.join(
                (Script.BASE_COMMAND, name) + tuple(f'<{arg}>' for arg in properties.args)
            ))

        python_print()
        exit()

    def check_args(self, args: Tuple[str], n: int = 0, exact: bool = True) -> None:
        n += 2  # Script name is always passed and command must be passed every time

        if len(args) < n or exact and len(args) != n:
            self.usage()

    def call(self, args: Tuple[str]) -> None:
        self.check_args(args, exact=False)

        command: Script.CommandProperties
        try:
            command = self.commands[args[1]]
        except KeyError:
            self.usage()

        self.check_args(args, len(command.args))

        command.callable(*args[2:])


def print_hexstring(str_: str, columns: int = 32, group_by: int = 4) -> None:
    i: Iterator[str] = iter(str_)

    while True:
        for _ in range(group_by):
            for _ in range(columns):
                try:
                    python_print(next(i), end='')
                except StopIteration:
                    return
            python_print()
        python_print()


def bytes_to_hexstring(b: bytes) -> str:
    return ''.join(f'{byte:02x}' for byte in b)


# noinspection PyShadowingBuiltins
def print(filename: str) -> None:
    python_print()

    with open(filename, 'rb') as f:
        print_hexstring(bytes_to_hexstring(f.read()))


def mct_mfd(in_filename: str, out_filename: str) -> None:
    with open(in_filename) as in_, open(out_filename, 'wb') as out:
        out.write(bytes.fromhex(''.join(line.strip() for line in in_ if not line.startswith('+'))))


script: Script = Script(
    print,
    mct_mfd
)


if __name__ == '__main__':
    script.call(sys.argv)
