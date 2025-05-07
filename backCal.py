from typing import Tuple, Any

from dots import *
import getCurve
from dots import dotList


def findIntersect(a: Dot, b: Dot, aDeg: float, bDeg: float, allowNeg=False):
    """
    value of deg (same as in Minecraft):
        z+: 0, x+: -90
    point shot from (0, 0) with deg by L:
        L *　(-sin(deg), cos(deg))
    :returns: (intersection, (distance from a, distance from b)). None if no intersection
    """
    D = 1 / sinD(bDeg - aDeg)
    T = cosD(aDeg) * (b.x - a.x) + sinD(aDeg) * (b.z - a.z)
    T *= D
    S = cosD(bDeg) * (b.x - a.x) + sinD(bDeg) * (b.z - a.z)
    S *= D

    if not allowNeg and ((T < 0) or (S < 0)):
        return None

    P1 = a.moveFor(aDeg, S)
    # equals to: P2 = b.moveFor(bDeg, T)

    # assert veryClose(P1, P2)
    return (P1, (T, S))


def getSt(a, b) -> dotList:
    pts = getCurve.straight(a, b)
    pts.toInt()
    return pts


def getBz(a, c1, c2, b) -> dotList:
    pts = getCurve.bz(a, c1, c2, b)
    pts.toInt()
    return pts
