import generator
import render

import sys

# in default value, the result is around (91, 38)
def get45BzPoints(R=128):
    s2 = 2 ** 0.5
    dx = R / (1 + s2)
    dz = R / (2 + s2)
    dx32 = dx * 2/3
    dz31 = dz / 3
    return (0, 0), (dx + dz, dz)

def main():
    ## specify positions
    a = [0, 0]
    b = [50, 50]
    aDeg = -90
    bDeg = 0
    ## specify block types
    block_for_ground = "quartz_block"
    block_under_rail = "diorite"
    ## specify options
    place_rail = True
    place_arrow = False
    ## select render mode
    dots = render.BZC_ANY(a, b, aDeg, bDeg)
    # dots = render.BZC_R(a, b, xFirst=True)
    # dots = render.BZC_S(a, b, mainX=False)
    ## debug
    # print(dots)

    generator.putCmdSingle(dots, block_for_ground, block_under_rail, place_rail, place_arrow)

def mainHeight():
    L = [round(-15 * (c - 1) / 23 + 85 - 70) for c in range(25)]
    generator.putHigh(L, -1, -1)

if __name__ == '__main__':
    main()
