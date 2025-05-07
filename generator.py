# execute as @e[type=armor_stand, tag=build, sort=nearest] at @s run tp ~x ~ ~z
base = "execute as @e[type=armor_stand, tag=build, sort=nearest] at @s run"


def setCord(p1: tuple, p2: tuple):
    return f" fill ~" + ' ~'.join([f"{c}" for c in p1]) + ' ~' + ' ~'.join([f"{c}" for c in p2]) + ' '

def showDict(d: dict):
    s = "# "
    for c in d:
        s += f"{c}: {d[c]},"
    return s[:-1]

def placeArrow(length, xp, zp):
    # ... magenta_glazed_terracotta[facing=north]
    '''
         n
     w       e(x+)
        s(z+)
    '''
    # begin check
    astx = (xp == 1 or xp == -1) and (zp == 0)
    astz = (zp == 1 or zp == -1) and (xp == 0)
    assert (astx) != (astz)
    # end check
    global base
    mgt = 'magenta_glazed_terracotta[facing='
    dir = {
        (1, 0): 'west',
        (-1, 0): 'east',
        (0, 1): 'north',
        (0, -1): 'south'
    }
    if zp != 0:
        length = zp * (length - 1)
        cordL = base + setCord((zp, -1, zp), (zp, -1, length)) + mgt
        cordR = base + setCord((-zp, -1, zp), (-zp, -1, length)) + mgt
    else:  # xp != 0
        length = xp * (length - 1)
        cordL = base + setCord((xp, -1, -xp), (length, -1, -xp)) + mgt
        cordR = base + setCord((xp, -1, xp), (length, -1, xp)) + mgt
    print(cordL + dir[(-zp, xp)] + ']')
    print(cordR + dir[(zp, -xp)] + ']')


def dig(length, r, h, mainX):
    global base
    one = toPN(length >= 0)
    if mainX:
        cordC = base + setCord((-one, h, r), (length, h, -r))  # ceil, replacing falling block
        cordD = base + setCord((-one, 0, r), (length, h - 1, -r))  # to dig
        cordG = base + setCord((0, -1, r), (length - one, -1, -r))  # to place for ground
        cordM = base + setCord((0, -1, 0), (length, -1, 0))  # to place under rail / central
    else:
        cordC = base + setCord((r, h, -one), (-r, h, length))
        cordD = base + setCord((r, 0, -one), (-r, h - 1, length))
        cordG = base + setCord((r, -1, 0), (-r, -1, length - one))
        cordM = base + setCord((0, -1, 0), (0, -1, length))
    # print(cordC + "stone replace gravel")
    # print(cordC + "smooth_sandstone replace sand")
    # print(cordC + "blue_stained_glass replace water")
    # print(cordD + "air")
    # print(cordG + "smooth_quartz")
    print(cordM + "smooth_quartz")
    print(base + " setblock ~ ~2 ~ glowstone")
    placeArrow((length if length >= 0 else -length), (one if mainX else 0), (0 if mainX else one))


# print(cordM + "rail")

def digSingle(length, h, mainX, r=1):
    global base
    one = toPN(length >= 0)
    cordC = ["", ""]
    cordD = ["", ""]
    cordG = ["", ""]
    if mainX:
        cordC[0] = base + setCord((0, h, r), (length, h, -r))  # ceil
        cordC[1] = base + setCord((-one, h, 0), (length + one, h, 0))  # ceil
        cordD[0] = base + setCord((0, h - 1, r), (length, 0, -r))  # dig
        cordD[1] = base + setCord((-one, h - 1, 0), (length + one, 0, 0))  # dig
        cordG[0] = base + setCord((0, -1, r), (length, -1, -r))  # ground
        cordG[1] = base + setCord((-one, -1, 0), (length + one, -1, 0))  # ground
        cordM = base + setCord((0, -1, 0), (length, -1, 0))  # central(under rail)
    else:
        cordC[0] = base + setCord((r, h, 0), (-r, h, length))  # ceil
        cordC[1] = base + setCord((0, h, -one), (0, h, length + one))  # ceil
        cordD[0] = base + setCord((r, h - 1, 0), (-r, 0, length))  # dig
        cordD[1] = base + setCord((0, h - 1, -one), (0, 0, length + one))  # dig
        cordG[0] = base + setCord((r, -1, 0), (-r, -1, length))  # ground
        cordG[1] = base + setCord((0, -1, -one), (0, -1, length + one))  # ground
        cordM = base + setCord((0, -1, 0), (0, -1, length))  # central(under rail)
    for c in ["stone replace gravel", "smooth_sandstone replace sand", "stone replace gravel"]:
        print(cordC[0] + c)
        print(cordC[1] + c)
    for i in (0, 1):
        print(cordD[i] + "air")
        print(cordG[i] + "gray_concrete keep")
    # print(cordCW + "stone replace gravel")
    # print(cordCW + "smooth_sandstone replace sand")
    # print(cordCW + "blue_stained_glass replace water")
    # print(cordCF + "stone replace gravel")
    # print(cordCF + "smooth_sandstone replace sand")
    # print(cordCF + "blue_stained_glass replace water")
    # print(cordDW + "air")
    # print(cordDF + "air")
    print(cordM + "quartz_block")
    #if not (-1 <= length <= 1):
    #    placeArrow((length if length >= 0 else -length), (one if mainX else 0), (0 if mainX else one))


def putCmd(Ls: tuple[dict, list], r=1, h=2):
    # print(f"# from: {Ls[0]}, to: {Ls[1]}")
    print(showDict(Ls[0]))
    L = Ls[1]
    global base
    if len(L) >= 2048:
        raise Exception("Required commands are too many")
    for c in L:
        if c[0] == 0:  # c[0] == 1 or c[0] == -1:  # z main
            dig(c[1], r, h, False)
        else:
            dig(c[0], r, h, True)
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print("tag @e[type=armor_stand, tag=build, sort=nearest] remove build")


def putCmdSingle(Ls: tuple[dict, list], h=2):
    # print(f"# from: {Ls[0]}, to: {Ls[1]}")
    print(showDict(Ls[0]))
    L = Ls[1]
    global base
    if len(L) >= 2048:
        raise Exception("Required commands are too many")
    for c in L:
        if c[0] == 0:  # z main
            digSingle(c[1], h, False)
        else:
            digSingle(c[0], h, True)
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print("tag @e[type=armor_stand, tag=build, sort=nearest] remove build")


def toPN(pos: bool):
    return 1 if pos else -1


def putHigh(L: list[int], xp, zp, block="white_stained_glass"):
    # begin check
    # astx = (xp == 1 or xp == -1) and (zp == 0)
    # astz = (zp == 1 or zp == -1) and (xp == 0)
    # assert (astx) != (astz)
    # end check
    global base
    for c in L:
        print(base + f" setblock ~ ~{c} ~ {block}")
        print(base + f" tp ~{xp} ~ ~{zp}")
    print("tag @e[type=armor_stand, tag=build, sort=nearest] remove build")


if __name__ == '__main__':
    args = [10, 5, 2, True]
    s1 = dig(*args)
    print()
    putCmd((0, 0, [(0, 2), (1, 0), (0, 1)]), 2, 2)
