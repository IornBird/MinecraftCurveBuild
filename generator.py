# execute as @e[type=armor_stand, tag=build, sort=nearest] at @s run tp ~x ~ ~z
from enum import Enum
import math

from buildOpt import BuildOpt, Block


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


def showDict(d: dict):
    s = "# "
    for c in d:
        s += f"{c}: {d[c]},"
    return s[:-1]


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

    def getPosCoord(self, Yield=True):
        headX = self.one * 2 if Yield else 0
        if Yield and -2 < self.length < 2:
            return None
        Begin = [headX, self.heightBegin, self.width]
        End = [self.length, self.heightEnd, self.width]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getNegCoord(self, Yield=True):
        headX = self.one * 2 if Yield else 0
        if Yield and -2 < self.length < 2:
            return None
        Begin = [headX, self.heightBegin, -self.width]
        End = [self.length, self.heightEnd, -self.width]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        return Begin, End

    def getWrapCoord(self, prev=0):
        Begin = [self.length + self.one, self.heightBegin, 1]
        End = [self.length + self.one, self.heightEnd, -1]
        if not self.mainX:
            Begin.reverse()
            End.reverse()
        Ans = [self.getPosCoord(prev < 0), self.getNegCoord(prev > 0), [Begin, End]]
        return [c for c in Ans if c]

    def getCentCoord(self, Yield=True):
        headX = self.one if Yield else 0
        Begin = [headX, self.heightBegin, 0]
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
    def __init__(self, command_generator: CommandGenerator, opt: BuildOpt,
                 width: int = 1, height: int = 2):
        self.cmd_gen = command_generator
        self.opt = opt
        self.width = width
        self.height = height
        self.prevDir = 0

    def generate_ceiling_commands(self, coords: CoordinateCalculator) -> list[str]:
        if self.opt.wrap:  # Skip ceiling commands if wrapped
            return []
        org_block = ["stone", "smooth_sandstone", "blue_stained_glass"]
        rep_block = ["gravel", "sand", "water"]
        points = coords.setHeight(self.height + 1, self.height + 1).getBothCoord(False)
        cmds = []
        for i in range(len(org_block)):
            for pt in points:
                cmds.append(self.cmd_gen.generate_fill_command(
                    *pt, block=org_block[i], state=FillState.REPLACE(rep_block[i])
                ))
        return cmds

    def generate_dig_commands(self, coords: CoordinateCalculator) -> list[str]:
        points = coords.setHeight(0, self.height).setWidth(self.width).getBothCoord()
        cmds = []
        for j in (0, 1):
            cmds.append(self.cmd_gen.generate_fill_command(
                *points[j], block="air"
            ))
        return cmds

    def generate_wrap_commands(self, coords: CoordinateCalculator) -> list[str]:
        if not self.opt.wrap:
            return []
        # create ceil
        cmds = []
        points = coords.setHeight(self.height + 1, self.height + 1).getBothCoord(False)
        for pt in points:
            cmds.append(self.cmd_gen.generate_fill_command(
                *pt, block=str(self.opt.wBlock)
            ))
        # create solid cuboid
        points = coords.setHeight(-1, self.height + 1).setWidth(self.width + 1).getWrapCoord(self.prevDir)
        for pt in points:
            cmds.append(self.cmd_gen.generate_fill_command(
                *pt, block=str(self.opt.wBlock)
            ))
        return cmds

    def generate_arrow_command(self, coords: CoordinateCalculator, point: tuple[int, int]) -> list[str]:
        # begin check
        xp, zp = point
        astx = (xp == 1 or xp == -1) and (zp == 0)
        astz = (zp == 1 or zp == -1) and (xp == 0)
        assert (astx) != (astz)
        # end check
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
            length = coords.length
            points = [
                [(zp, -1, zp), (zp, -1, length)],
                [(-zp, -1, zp), (-zp, -1, length)],
                [(0, -1, length + zp), (0, -1, length + zp)]
            ]
        else:  # xp != 0
            length = coords.length
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

    def generate_ground_commands(self, coords: CoordinateCalculator) -> list[str]:
        points = coords.setHeight(-1, -1).getBothCoord()
        cmds = []
        for pt in points:
            cmds.append(self.cmd_gen.generate_fill_command(
                *pt, block=str(self.opt.gBlock), state=FillState.KEEP
            ))
        return cmds

    def generate_rail_commands(self, coords: CoordinateCalculator) -> list[str]:
        points = [
            coords.setHeight(-1, -1).getCentCoord(),
            coords.setHeight(0, 0).getCentCoord()
        ]
        blocks = [str(self.opt.rBlock), "rail"]
        cmds = []
        for i in range(len(points)):
            cmds.append(self.cmd_gen.generate_fill_command(
                *points[i], block=blocks[i]
            ))
        return cmds

    # public
    def build_railway_segment(self, length: int, mainX: bool) -> list[str]:
        one = toPN(length >= 0)
        coords = CoordinateCalculator(length, mainX, self.width, self.height)
        cmds = []
        if self.opt.wrap:
            cmds.extend(self.generate_wrap_commands(coords))
        else:
            cmds.extend(self.generate_ceiling_commands(coords))
        cmds.extend(self.generate_dig_commands(coords))
        if self.opt.place_arrow:
            cmds.extend(self.generate_arrow_command(coords, (one, 0) if mainX else (0, one)))
        else:
            cmds.extend(self.generate_ground_commands(coords))
        if self.opt.place_rail:
            cmds.extend(self.generate_rail_commands(coords))
        self.prevDir = length
        return cmds


def putCmdDouble(Ls: tuple[dict, list], opt: BuildOpt, r=2, h=3):
    """
    organized version
    main function to print mcfunction file building known curve
    the curve is for two_way rail
    """
    raise NotImplementedError("This function has not yet implemented")
    print(showDict(Ls[0]))
    L = Ls[1]
    if len(L) >= 2048:
        raise Exception("Required commands are too many")
    entity = "@e[type=armor_stand, tag=build, sort=nearest]"
    base = f"execute as {entity} at @s run"
    builder = RailwayBuilder(CommandGenerator(entity), opt, r, h)
    implement = False
    for c in L:
        mainX = (c[0] != 0)
        implement = not ((-1 <= c[not mainX] <= 1) and implement)
        if implement:
            cmds = builder.build_railway_segment(c[not mainX], mainX)
            print('\n'.join(cmds))
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print(f"tag {entity} remove build")

def putCmdSingle(Ls: tuple[dict, list], opt: BuildOpt, r=1, h=2):
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
    base = f"execute as {entity} at @s run"
    builder = RailwayBuilder(CommandGenerator(entity), opt, r, h)
    for c in L:
        mainX = (c[0] != 0)
        cmds = builder.build_railway_segment(c[not mainX], mainX)
        print('\n'.join(cmds))
        print(base + f" tp ~{c[0]} ~ ~{c[1]}")
    print(f"tag {entity} remove build")


def toPN(pos: bool):
    return 1 if pos else -1


def putHigh(L: list[int], xp, zp, half=False, block="white_stained_glass"):
    # begin check
    # astx = (xp == 1 or xp == -1) and (zp == 0)
    # astz = (zp == 1 or zp == -1) and (xp == 0)
    # assert (astx) != (astz)
    # end check
    entity = "@e[type=armor_stand, tag=build, sort=nearest]"
    base = f"execute as {entity} at @s run"
    for c in L:
        if half:
            rc = math.floor(c)
            top = "[type=top]" if (rc != c) else ""
            print(base + f" setblock ~ ~{rc} ~ {block}" + top)
        else:
            print(base + f" setblock ~ ~{c} ~ {block}")
        print(base + f" tp ~{xp} ~ ~{zp}")
    print(f"tag {entity} remove build")


if __name__ == '__main__':
    args = [(10, 0), (0, -1), (1, 0), (0, -1), (1, 0), (0, -5)]  # [(0, 10), (-1, 0), (0, 5)]
    opt = BuildOpt(Block("stone"), Block("quartz_block"), place_rail=True, place_arrow=True, wrap=True)
    putCmdSingle([{"test": str(args)}, args], opt)
    # putCmdDouble([{"test": "test"}, args], "stone", "quartz_block", True)
