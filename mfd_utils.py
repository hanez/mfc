import inspect
import sys
from collections import namedtuple


class Script:
    BASE_COMMAND = f'python3 {__file__}'
    CommandProperties = namedtuple('CommandProperties', ('args', 'callable'))

    def __init__(self, *commands):
        self.commands = {
            command.__name__: Script.CommandProperties(
                tuple(inspect.signature(command).parameters.keys()),
                command
            ) for command in commands
        }

    def usage(self):
        print()

        print('Usage:')
        for name, properties in self.commands.items():
            print('\t' + ' '.join(
                (Script.BASE_COMMAND, name) + tuple(f'<{arg}>' for arg in properties.args)
            ))

        print()
        exit()

    def call(self, args):
        if len(args) < 2:  # program name and command
            self.usage()

        try:
            command = self.commands[args[1]]
        except KeyError:
            self.usage()

        if len(args) != 2 + len(command.args):
            self.usage()

        command.callable(*args[2:])


def grouper(iterable, n):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip(*args)


def print_hexstring(str, columns, group_by):
    i = iter(str)

    while True:
        for _ in range(group_by):
            for _ in range(columns):
                try:
                    print(next(i), end='')
                except StopIteration:
                    return
            print()
        print()


def bytes_to_hexstring(b):
    return ''.join(f'{byte:02x}' for byte in b).upper()


def print_mfd(filename):
    print()

    with open(filename, 'rb') as f:
        print_hexstring(bytes_to_hexstring(f.read()), 32, 4)


def mct_mfd(in_filename, out_filename):
    with open(in_filename, encoding='ascii') as in_, open(out_filename, 'wb') as out:

        # for each header and the following 4 lines in the file
        #   key: Keep only the index of the sector as int
        #   value: A hex string representing the sector data

        sectors = {
            int(header.strip().replace('+Sector: ', '')): ''.join(map(str.strip, data))
            for header, *data in grouper(in_, 1 + 4)
        }

        # write joined data for each of the 16 sectors
        out.write(bytes.fromhex(''.join(map(sectors.get, range(16)))))


def mfd_mct(in_filename, out_filename):
    with open(in_filename, 'rb') as in_, open(out_filename, 'w+', encoding='ascii') as out:
        # Create 16 sectors sections, each with a header and data
        for sector in range(16):
            out.write(f'+Sector: {sector}\n')

            for _ in range(4):  # 4 lines of data per sector
                out.write(bytes_to_hexstring(in_.read(16)) + '\n')

        out.truncate(2372)  # removing the last \n. 2372 is the size in bytes of a complete mct file.


def mct_c(filename):
    with open(filename, encoding='ascii') as f:
        sectors = (
            map(''.join, grouper(line, 2))
            for _, *data in grouper(f, 1 + 4)
            for line in data
        )

        print()
        print('byte data[64][16] = {')
        print(',\n'.join(f'  {{{", ".join("0x" + byte for byte in sector)}}}' for sector in sectors))
        print('};')
        print()


script: Script = Script(
    print_mfd,
    mct_mfd,
    mfd_mct,
    mct_c
)


if __name__ == '__main__':
    script.call(sys.argv)
