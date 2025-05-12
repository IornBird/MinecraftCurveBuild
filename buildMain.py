import generator
import render

import sys

def get45BzPoints(R=128):
    s2 = 2 ** 0.5
    dx = R / (1 + s2)
    dz = R / (2 + s2)
    dx32 = dx * 2/3
    dz31 = dz / 3
    return (0, 0), (dx + dz, dz)

def main():
    # x, y = get45BzPoints(128)  # around (91, 38)
    a = [458, -145]
    b = [484, -280]
    aDeg = -90
    bDeg = 45

    dots = render.BZC_ANY(a, b, aDeg, bDeg)
    # dots = render.BZC_R(a, b, xFirst=True)
    # dots = render.BZC_S(a, b, mainX=False)
    # print(dots)
    generator.putCmdSingle(dots)

def mainHeight():
    L = [round(-15 * (c - 1) / 23 + 85 - 70) for c in range(25)]
    generator.putHigh(L, -1, -1)

if __name__ == '__main__':
    main()
