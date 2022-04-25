import collections
import itertools
import os
import png
import sys

def _chunks(seq, n):
    assert n > 0
    assert len(seq) % n == 0, f'{len(seq)} % {n}'
    return tuple(tuple(seq[i:i+n]) for i in range(0, len(seq), n))

def _init_colors():
    with open('pallet-blocks.txt') as pallet_txt:
        blocks = pallet_txt.read().splitlines()
    image = png.Reader(filename='pallet.png')
    width, height, rows, info = image.asRGBA()
    pixels = _chunks(next(rows), 4)
    assert height == 1
    assert len(pixels) == len(blocks), f'{len(pixels)} == {len(blocks)}'
    assert len(pixels[0]) == 4
    res = {pixel: block for pixel, block in zip(pixels, blocks)}
    res[(0, 0, 0, 255)] = 'black_concrete'
    res[(255, 255, 255, 255)] = 'white_concrete'
    return res

__color2block = _init_colors()
#print(__color2block)

__planes = {
    'YZ': { 'delta_row': (0, 1, 0), 'delta_col': (0, 0, -1) },
    'YX': { 'delta_row': (0, 1, 0), 'delta_col': (-1, 0, 0) },
}

def color2block(color):
    block = __color2block.get(color)
    if block is None:
        sys.exit(f'Missing block for color {color}')
    return block

def image2pixels(filename):
    image = png.Reader(filename=filename)
    width, height, rows, info = image.asRGBA()
    pixels = [ _chunks(tuple(r), 4) for r in rows ]
    assert len(pixels) == height
    assert len(pixels[0]) == width
    return pixels

def image2blocks(filename):
    pixels = image2pixels(filename)
    return [ [ color2block(c) for c in r ] for r in pixels ]

def tuple_add(v1, v2):
    assert len(v1) == len(v2)
    return tuple(map(sum, zip(v1, v2)))

def find_most_common_block(blocks):
    frequency_map = collections.Counter(itertools.chain(*blocks))
    return max(frequency_map.items(), key=lambda x: x[1])[0]

def make_fill_command(origin, blocks, delta_row, delta_col, default_block):
    row_count = len(blocks)-1
    col_count = len(blocks[0])-1
    row_offset = tuple(x * row_count for x in delta_row)
    col_offset = tuple(x * col_count for x in delta_col)
    destination = tuple_add(tuple_add(row_offset, col_offset), origin)
    x0, y0, z0 = origin
    x1, y1, z1 = destination
    return f'fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:{default_block} replace'

def image2commands(filename, origin, delta_row=(0, 1, 0), delta_col=(0, 0, 1)):
    blocks = image2blocks(filename)
    blocks.reverse()
    default_block = find_most_common_block(blocks)
    position = origin
    commands = [ make_fill_command(origin, blocks, delta_row, delta_col, default_block) ]
    for row in blocks:
        row_origin = position
        for block in row:
            x, y, z = position
            if block != default_block:
                commands.append(f'setblock {x} {y} {z} minecraft:{block}')
            position = tuple_add(position, delta_col)
        position = tuple_add(row_origin, delta_row)
    return commands

def main():
    _, png_path, x, y, z = sys.argv
    origin = tuple(map(int, (x, y, z)))
    plane_name = os.environ.get('PLANE', 'YZ').upper()
    plane = __planes.get(plane_name)
    for cmd in image2commands(png_path, origin, plane['delta_row'], plane['delta_col']):
        print(cmd)

if __name__ == "__main__":
    main()
