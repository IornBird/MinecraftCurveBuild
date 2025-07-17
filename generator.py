# execute as @e[type=armor_stand, tag=build, sort=nearest] at @s run tp ~x ~ ~z
from enum import Enum
import math

entity = "@e[type=armor_stand, tag=build, sort=nearest]"
base = f"execute as {entity} at @s run"


def setCord(p1: tuple, p2: tuple):
    return f" fill ~" + ' ~'.join([f"{c}" for c in p1]) + ' ~' + ' ~'.join([f"{c}" for c in p2]) + ' '


def toOption(**kwargs):
    if not kwargs:
        return " "
    s = "["
    for c in kwargs:
        s += f"{c}={kwargs[c]},"
    return s[:-1] + "] "


class FillState(str):  # hard to inherit Enum for type detection
    DEFAULT: str = ""
    KEEP: str = "keep"

    @classmethod
    def REPLACE(cls, s: str) -> str:
        return f"replace {s}"


def fillRelative(p1: tuple, p2: tuple, block, state: str=FillState.DEFAULT, **kwargs):
    return base + setCord(p1, p2) + block + toOption(**kwargs) + state


def showDict(d: dict):
    s = "# "
    for c in d:
        s += f"{c}: {d[c]},"
    return s[:-1]


def placeArrow(length, xp, zp, Yield=True):
    """
    print command to place arrows around and point toward railway
    For Flashteen's bulletcart, arrows prevent cart from derailment when moving too fast.
    """
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
        length = zp * (length)
        cordL = base + setCord((zp, -1, zp), (zp, -1, length)) + mgt
        cordR = base + setCord((-zp, -1, zp), (-zp, -1, length)) + mgt
        cordH = base + setCord((0, -1, length + zp), (0, -1, length + zp)) + mgt
    else:  # xp != 0
        length = xp * (length)
        cordL = base + setCord((xp, -1, -xp), (length, -1, -xp)) + mgt
        cordR = base + setCord((xp, -1, xp), (length, -1, xp)) + mgt
        cordH = base + setCord((length + xp, -1, 0), (length + xp, -1, 0)) + mgt
    s = cordL + dir[(-zp, xp)] + ']\n'
    s += cordR + dir[(zp, -xp)] + ']\n'
    s += cordH + dir[(-xp, -zp)] + ']'
    return s


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


class Coord:
    def __init__(self, length: int, mainX: bool, w=1, h=2):
        self.one = toPN(length >= 0)
        self.mainX = mainX
        self.length = length
        self.width = w
        self.heightBegin = 0
        self.heightEnd = h

    def setWidth(self, w=1):
        self.width = w

    def setHeight(self, hBegin=0, hEnd=2):
        self.heightBegin = hBegin
        self.heightEnd = hEnd

    def getWideCoord(self, Yield=True):
        headX = self.one if Yield else 0
        Begin = [headX, self.heightBegin, self.width]
        End = [self.length, self.heightEnd, -self.width]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getDeepCoord(self, Yield=True):
        headX = self.one if Yield else -self.one
        Begin = [headX, self.heightBegin, 0]
        End = [self.length + self.one, self.heightEnd, 0]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getOrgCoord(self):
        Begin = [0, self.heightBegin, 0]
        End = [self.length, self.heightEnd, 0]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def fillCmd(self, hBeg, hEnd, Yield, block, state=FillState.DEFAULT, **kwargs):
        self.setHeight(hBeg, hEnd)
        return fillRelative(
            *self.getDeepCoord(Yield), block=block, state=state, **kwargs
        ) + '\n' + fillRelative(
            *self.getWideCoord(Yield), block=block, state=state, **kwargs
        )

    def fillArrowCmd(self):
        return placeArrow(
            (math.fabs(self.length)),
            (self.one if self.mainX else 0), (0 if self.mainX else self.one)
        )

    def fillDeepCmd(self, hBeg, hEnd, Yield, block, state=FillState.DEFAULT, **kwargs):
        self.setHeight(hBeg, hEnd)
        return fillRelative(
            *self.getDeepCoord(Yield), block=block, state=state, **kwargs
        )


def digSingle(length: int, mainX: bool, gBlock, rBlock, rail=True, arrow=False, r=1, h=2):
    """
    print multiple fill command for part of curve for railway
    """
    global base
    coord = Coord(length, mainX)
    coord.setWidth(r)

    # ceil
    coord.setHeight(h + 1, h + 1)
    cordC = [
        coord.getDeepCoord(False),
        coord.getWideCoord(False)
    ]
    fallings = [
        ["stone", "gravel"],
        ["smooth_sandstone", "sand"],
        ["blue_stained_glass", "water"]
    ]
    ceil = ""
    for c in fallings:
        for b in (0, 1):
            ceil += fillRelative(*cordC[b], block=c[0], state=FillState.REPLACE(c[1])) + '\n'
    ceil = ceil[:-1]
    dig = coord.fillCmd(0, h, True, "air")
    if arrow:
        ground = coord.fillArrowCmd()
    else:
        ground = coord.fillCmd(-1, -1, False, gBlock, state=FillState.KEEP)
    coord.setHeight(-1, -1)
    underRail = fillRelative(*coord.getOrgCoord(), block=rBlock)
    coord.setHeight(0, 0)
    if rail:
        railCmd = fillRelative(*coord.getOrgCoord(), block="rail")

    args = [ceil, dig, ground, underRail]
    if rail:
        args.append(railCmd)
    print(*args, sep='\n')


class CoordinateCalculator:
    def __init__(self, length: int, mainX: bool, width: int = 1, height: int = 2):
        self.one = toPN(length >= 0)
        self.mainX = mainX
        self.length = length
        self.width = width
        self.heightBegin = 0
        self.heightEnd = height

    def setWidth(self, w=1):
        self.width = w
        return self

    def setHeight(self, hBegin=0, hEnd=2):
        self.heightBegin = hBegin
        self.heightEnd = hEnd
        return self

    def getWideCoord(self, Yield=True):
        headX = self.one if Yield else 0
        Begin = [headX, self.heightBegin, self.width]
        End = [self.length, self.heightEnd, -self.width]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getDeepCoord(self, Yield=True):
        headX = self.one if Yield else -self.one
        Begin = [headX, self.heightBegin, 0]
        End = [self.length + self.one, self.heightEnd, 0]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getBothCoord(self, Yield=True):
        return self.getDeepCoord(Yield), self.getWideCoord(Yield)

    def getOrgCoord(self):
        Begin = [0, self.heightBegin, 0]
        End = [self.length, self.heightEnd, 0]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End


class CommandGenerator:
    def __init__(self, entity_selector: str):
        self.entity = entity_selector
        self.base = f"execute as {self.entity} at @s run"

    def generate_fill_command(self, start: tuple, end: tuple,
                              block: str, state: str = FillState.DEFAULT, **kwargs) -> str:
        return self.base + setCord(start, end) + block + toOption(**kwargs) + state


class RailwayBuilder:
    def __init__(self, command_generator: CommandGenerator,
                 ground_block: str, rail_block: str,
                 place_rail: bool = True,
                 place_arrow: bool = False,
                 width: int = 1, height: int = 2):
        self.cmd_gen = command_generator
        self.gBlock = ground_block
        self.rBlock = rail_block
        self.place_arrow = place_arrow
        self.place_rail = place_rail
        self.width = width
        self.height = height

    def generate_ceiling_commands(self, coords: CoordinateCalculator) -> list[str]:
        org_block = ["stone", "smooth_sandstone", "blue_stained_glass"]
        rep_block = ["gravel", "sand", "water"]
        points = coords.setHeight(self.height + 1, self.height + 1).getBothCoord(False)
        cmds = []
        for i in range(len(org_block)):
            for j in (0, 1):
                cmds.append(self.cmd_gen.generate_fill_command(
                    *points[j], block=org_block[i], state=FillState.REPLACE(rep_block[i])
                ))
        return cmds

    def generate_dig_commands(self, coords: CoordinateCalculator) -> list[str]:
        points = coords.setHeight(0, self.height).getBothCoord(False)
        cmds = []
        for j in (0, 1):
            cmds.append(self.cmd_gen.generate_fill_command(
                *points[j], block="air"
            ))
        return cmds

    def generate_arrow_command(self, coords: CoordinateCalculator, point: tuple[int, int]) -> list[str]:
        # begin check
        xp, zp = point
        astx = (xp == 1 or xp == -1) and (zp == 0)
        astz = (zp == 1 or zp == -1) and (xp == 0)
        assert (astx) != (astz)
        # end check
        global base
        mgt = 'magenta_glazed_terracotta'
        dir = {
            (1, 0): 'west',
            (-1, 0): 'east',
            (0, 1): 'north',
            (0, -1): 'south'
        }
        dirs = [
            (-zp, xp),
            (zp, -xp),
            (-xp, -zp)
        ]
        if zp != 0:
            length = zp * coords.length
            points = [
                [(zp, -1, zp), (zp, -1, length)],
                [(-zp, -1, zp), (-zp, -1, length)],
                [(0, -1, length + zp), (0, -1, length + zp)]
            ]
        else:  # xp != 0
            length = xp * coords.length
            points = [
                [(xp, -1, -xp), (length, -1, -xp)],
                [(xp, -1, xp), (length, -1, xp)],
                [(length + xp, -1, 0), (length + xp, -1, 0)]
            ]
        cmds = []
        for i in range(3):
            cmds.append(self.cmd_gen.generate_fill_command(
                points[i][0], points[i][1], mgt, facing=dir[dirs[i]]
            ))
        return cmds

    def generate_ground_commands(self, coords: CoordinateCalculator, block: str, **kwargs) -> list[str]:
        points = coords.setHeight(-1, -1).getBothCoord()
        cmds = []
        for j in (0, 1):
            cmds.append(self.cmd_gen.generate_fill_command(
                *points[j], block=block, state=FillState.KEEP, **kwargs
            ))
        return cmds

    def generate_rail_commands(self, coords: CoordinateCalculator, block: str, **kwargs) -> list[str]:
        points = [
            coords.setHeight(-1, -1).getOrgCoord(),
            coords.setHeight(0, 0).getOrgCoord()
        ]
        blocks = [block, "rail"]
        states = [kwargs, dict()]
        cmds = []
        for i in range(len(points)):
            cmds.append(self.cmd_gen.generate_fill_command(
                *points[i], block=blocks[i], **(states[i])
            ))
        return cmds

    # public
    def build_railway_segment(self, length: int, mainX: bool) -> list[str]:
        one = toPN(length >= 0)
        coords = CoordinateCalculator(length, mainX, self.width, self.height)
        cmds = self.generate_ceiling_commands(coords)
        cmds.extend(self.generate_dig_commands(coords))
        if self.place_arrow:
            cmds.extend(self.generate_arrow_command(coords, (one, 0) if mainX else (0, one)))
        else:
            cmds.extend(self.generate_ground_commands(coords, self.gBlock))
        if self.place_rail:
            cmds.extend(self.generate_rail_commands(coords, self.rBlock))
        return cmds


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


def putCmdSingle(Ls: tuple[dict, list], gBlock, rBlock, placeRail=True, placeArrow=False, r=1, h=3):
    """
    main function to print mcfunction file building known curve
    the curve is for signal rail
    """
    print(showDict(Ls[0]))
    L = Ls[1]
    global base, entity
    if len(L) >= 2048:
        raise Exception("Required commands are too many")
    for c in L:
        mainX = (c[0] != 0)
        digSingle(c[not mainX], mainX, gBlock, rBlock, placeRail, placeArrow, r, h)
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print(f"tag {entity} remove build")


def putCmdSingleNew(Ls: tuple[dict, list], gBlock, rBlock, placeRail=True, placeArrow=False, r=1, h=3):
    """
    organized version
    main function to print mcfunction file building known curve
    the curve is for signal rail
    """
    print(showDict(Ls[0]))
    L = Ls[1]
    if len(L) >= 2048:
        raise Exception("Required commands are too many")
    entity = "@e[type=armor_stand, tag=build, sort=nearest]"
    builder = RailwayBuilder(CommandGenerator(entity), gBlock, rBlock, placeRail, placeArrow, r, h)
    for c in L:
        mainX = (c[0] != 0)
        cmds = builder.build_railway_segment(c[not mainX], mainX)
        print('\n'.join(cmds))
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print(f"tag {entity} remove build")

def toPN(pos: bool):
    return 1 if pos else -1


def putHigh(L: list[int], xp, zp, block="white_stained_glass"):
    # begin check
    # astx = (xp == 1 or xp == -1) and (zp == 0)
    # astz = (zp == 1 or zp == -1) and (xp == 0)
    # assert (astx) != (astz)
    # end check
    global base, entity
    for c in L:
        print(base + f" setblock ~ ~{c} ~ {block}")
        print(base + f" tp ~{xp} ~ ~{zp}")
    print(f"tag {entity} remove build")


if __name__ == '__main__':
    args = [(0, 10), (1, 0), (0, 5)]
    putCmdSingle([{"test": "test"}, args], "stone", "quartz_block", True)
    print("=" * 20)
    putCmdSingleNew([{"test": "test"}, args], "stone", "quartz_block", True)
