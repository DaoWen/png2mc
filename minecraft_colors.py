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

def image2commands(filename, origin, delta_row=(0, 1, 0), delta_col=(0, 0, 1)):
    blocks = image2blocks(filename)
    blocks.reverse()
    position = origin
    commands = []
    for row in blocks:
        row_origin = position
        for block in row:
            x, y, z = position
            commands.append(f'setblock {x} {y} {z} minecraft:{block}')
            position = tuple_add(position, delta_col)
        position = tuple_add(row_origin, delta_row)
    return commands

def main():
    _, png_path, x, y, z = sys.argv
    origin = tuple(map(int, (x, y, z)))
    for cmd in image2commands(png_path, origin):
        print(cmd)

if __name__ == "__main__":
    main()
