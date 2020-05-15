import abc
import argparse
import os
from itertools import chain


class Sector(abc.ABC):
    def __init__(self, data, key_a, ac, key_b):
        assert not any(map(bool, (data, key_a, ac, key_b))) or data and ac
        assert not  data or len(data)  == 48, "Invalid data length"
        assert not key_a or len(key_a) ==  6, "Invalid key A length"
        assert not    ac or len(ac)    ==  4, "Invalid access conditions length"
        assert not key_b or len(key_b) ==  6, "Invalid key B length"

        self.data = data
        self.key_a = key_a
        self.ac = ac
        self.key_b = key_b

    def __bool__(self):
        return bool(self.data) and bool(self.ac)

    def __bytes__(self):
        return self.data + self.key_a + self.ac + self.key_b

    def keys(self):
        return self.key_a, self.key_b


def error(msg):
    print(f'[ERROR] {msg}')
    exit(-1)


def warning(msg):
    print(f'[WARNING] {msg}')


def grouper(iterable, n):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEF', 3,) --> ABC DEF"
    args = [iter(iterable)] * n
    return zip(*args)


def load_mfd(path, fuzzy):
    size  = os.path.getsize(path)

    if fuzzy:
        size >= 1024 or error(f'Invalid file size ({size}). At least 1024 bytes required.')

    else:
        size == 1024 or error(f'Invalid file size ({size}). Only 1024 bytes allowed.')

    with open(path, 'rb') as f:
        for _ in range(16):
            yield Sector(f.read(48), f.read(6), f.read(4), f.read(6))


def load_key(f):
    data = f.read(12)

    if data == '-' * 12:
        return None

    else:
        return bytes.fromhex(data)


def load_mct(path):
    sectors = {}

    with open(path, encoding='ascii') as f:
        g = grouper(f, 4)

        for _ in range(16):
            try:
                header, *data = next(g)

            except StopIteration:
                break

            except UnicodeDecodeError:
                error("Not a Mifare Classic Tools dump")

            if not header.startswith('+Sector: '):
                error('Invalid dump, probably 4k dump. Only 1k dump allowed.')

            sectors[int(header.replace('+Sector: ', ''))] = Sector(
                bytes.fromhex(''.join(data)),
                load_key(f),
                bytes.fromhex(f.read(8)),
                load_key(f)
            )

            f.readline()

    for sector_n in range(16):
        yield sectors.get(sector_n, Sector(None, None, None, None))


def fill(dump, strict):
    not_found = error if strict else warning

    filled = (
        Sector( # Give errors and fill data
            sector.data or (not_found(f'Sector {number} not found!'), bytes(48))[1],
            sector.key_a or (sector.data and not_found(f'Key A sector {number} not found!'), bytes(6))[1],
            sector.ac or bytes(4),
            sector.key_b or (sector.data and not_found(f'Key B sector {number} not found!'), bytes(6))[1]
        )
        for number, sector in enumerate(dump)
    )

    if strict:
        filled = tuple(filled)

    return filled


def dump_bytes(dump):
    return b''.join(map(bytes, dump))


def store_mfd(dump, strict, path):
    dump = fill(dump, strict)

    with open(path, 'wb') as f:
        f.write(dump_bytes(dump))


def blocks(bts):
    return map(bytes, grouper(bts, 16))


def upper_hex(bts):
    return bts.hex().upper()


def key_repr(key):
    return upper_hex(key) if key else '-' * 12


def store_mct(dump, path):
    nl = '\n'  # Avoid syntax error

    with open(path, 'w+', encoding='ascii') as f:
        f.write('\n'.join(filter(None, (
            f'+Sector: {number}\n'
            f'{nl.join(upper_hex(block) for block in blocks(sector.data))}\n'
            f'{key_repr(sector.key_a)}{upper_hex(sector.ac)}{key_repr(sector.key_b)}'
            if sector else ''
            for number, sector in enumerate(dump)
        ))))


def store_c(dump, strict, path):
    dump = fill(dump, strict)

    with open(path, 'w+', encoding='ascii') as f:
        f.write('\nbyte data[64][16] = {\n')
        f.write(',\n'.join(
            f'  {{{", ".join(f"0x{byte:02X}" for byte in block)}}}'
            for block in blocks(dump_bytes(dump))
        ))
        f.write('\n};\n')


def store_keys(dump, path):
    with open(path, 'w+', encoding='ascii') as f:
        f.write('\n'.join(set(filter(None, map(key_repr, chain(*map(Sector.keys, dump)))))))


def convert(args):
    if args.input_format == 'mfd':
        dump = load_mfd(args.input_path, args.fuzzy)

    elif args.input_format == 'mct':
        dump = load_mct(args.input_path)

    dump = tuple(dump)

    if args.output_format == 'mfd':
        store_mfd(dump, args.strict, args.output_path)

    elif args.output_format == 'mct':
        store_mct(dump, args.output_path)

    elif args.output_format == 'c':
        store_c(dump, args.strict, args.output_path)

    elif args.output_format == 'keys':
        store_keys(dump, args.output_path)


def main():
    parser = argparse.ArgumentParser(description='MFC - MiFare classic Converter')

    parser.add_argument('input_format', choices=['mfd', 'mct'], help='input format')
    parser.add_argument('output_format', choices=['mfd', 'mct', 'c', 'keys'], help='output format')
    parser.add_argument('input_path')
    parser.add_argument('output_path')
    parser.add_argument('-s', '--strict', action='store_true', help='Fail on missing data (otherwise filled with zeros)')
    parser.add_argument('-f', '--fuzzy', action='store_true', help='Accept file sizes >= 1024 for mfd format')

    args = parser.parse_args()

    convert(args)


if __name__ == '__main__':
    main()
