# interface to get dots in curve from begin(a) to destination(b)
import math

import backCal
from dots import *
from dots import Dot, dotList


def BZC_S(a: list[int], b: list[int], mainX: bool) -> tuple[dict, list]:
    a, b = Dot(*a), Dot(*b)
    c = backCal.midPt(a, b)
    if mainX:
        c1 = Dot(c.x, a.z)
        c2 = Dot(c.x, b.z)
    else:
        c1 = Dot(a.x, c.z)
        c2 = Dot(b.x, c.z)
    pts = backCal.getBz(a, c1, c2, b)
    d = {
        "from": a,
        "to": b
    }
    return (d, pts.getOffset().toScalarList())


def BZC_R(a: list[int], b: list[int], xFirst: bool) -> tuple[dict, list]:
    a, b = Dot(*a), Dot(*b)
    c = midPt(a, b)
    if xFirst:
        c1 = Dot(c.x, a.z)
        c2 = Dot(b.x, c.z)
    else:
        c1 = Dot(a.x, c.z)
        c2 = Dot(c.x, b.z)
    pts = backCal.getBz(a, c1, c2, b)
    d = {
        "from": a,
        "to": b
    }
    return (d, pts.getOffset().toScalarList())


def BZC_ANY(a: list[int], b: list[int], aDeg: float, bDeg: float) -> tuple[dict, list]:
    a, b = Dot(*a), Dot(*b)
    p = backCal.findIntersect(a, b, aDeg, bDeg)
    if p is None:
        print("wrong direction")
        return None
    aDst = p[1][0]
    bDst = p[1][1]
    dst = min(aDst, bDst)
    p = p[0]

    ar = p.moveFor(aDeg, -dst)
    br = p.moveFor(bDeg, -dst)
    m = backCal.findIntersect(ar, br, aDeg + 90, bDeg + 90, allowNeg=True)
    assert -1e-12 < math.fabs(m[1][0]) - math.fabs(m[1][1]) < 1e-12
    R = math.fabs(m[1][0])

    cFind = (aDeg - bDeg + 180) % 360.0 - 180
    cFind = dst * (math.fabs(cFind) + 45) / 270
    c1 = ar.moveFor(aDeg, cFind)
    c2 = br.moveFor(bDeg, cFind)

    pts = backCal.getSt(a, ar)
    pts.extend(backCal.getBz(ar, c1, c2, br))
    pts.extend(backCal.getSt(br, b))

    d = {
        "from": a,
        "to": b,
        "R": round(R, 3),
        "pass": p
    }

    return (d, pts.getOffset().toScalarList())

def straight_3D(a: list[int], b:list[int]):
    pass
