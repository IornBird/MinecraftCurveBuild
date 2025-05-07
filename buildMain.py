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

def main(v):
    # x, y = get45BzPoints(128)  # around (91, 38)
    a = [458, -145]
    b = [484, -280]  # [-91, -38] #-x+z
    aDeg = -90
    bDeg = 45

    # arg = [[-1909, 1735], [-2163, 1990]], [[-1909, 1728], [-2170, 1990]]
    # a, b = arg[v]

    # dots = render.BZC_ANY(a, b, aDeg, bDeg)
    # dots = render.BZC_R(a, b, xFirst=True)
    dots = render.BZC_S(a, b, mainX=False)
    # print(dots)
    generator.putCmdSingle(dots)

def mainHeight():
    L = [round(-15 * (c - 1) / 23 + 85 - 70) for c in range(25)]
    generator.putHigh(L, -1, -1)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(int(sys.argv[1]))
    else:
        print("Args not enough")
    # mainHeight()
    # main()
