from dots import *


def getUnit(p1, p2, strict=True) -> dotList:
    r1, r2 = p1.round(), p2.round()
    if (not strict) or (r1.x == r2.x) or (r1.z == r2.z):
        pts = dotList(p1)
        pts.append(p2)
        return pts
    cent = midPt(r1, r2)
    v1 = cent - p1
    v2 = p2 - p1

    pts = dotList(p1)
    val = v1.cross(v2)  # pos iff v2 is left of v1 (z-axis to x-axis)

    bity = (val > 0)
    bitx = (v2.x > 0)
    bitz = (v2.z > 0)
    """
    bity bitx bitz | pos to-x
    1    1    1      1   1
    0    1    1      1   0
    1    1    0      0   0
    0    1    0      1   1
    1    0    1      1   0
    0    0    1      0   1
    1    0    0      0   1
    0    0    0      0   0   
    """
    if bitx == bitz:
        pos = bitx
        to_x = bity
    else:
        pos = (bity != bitx)
        to_x = not bity
    filler = {
        (1, 1): Dot(1, 0),
        (0, 1): Dot(-1, 0),
        (1, 0): Dot(0, 1),
        (0, 0): Dot(0, -1)
    }[(pos, to_x)]

    pts.append(r1 + filler)
    pts.append(p2)
    return pts


def bz(P1, P2, P3, P4, strict=True) -> dotList:
    # Bézier curve
    if close(P1, P4):
        return getUnit(P1, P4, strict)
    L1 = P1
    L2 = midPt(P1, P2)
    H = midPt(P2, P3)
    R3 = midPt(P3, P4)
    R4 = P4
    L3 = midPt(L2, H)
    R2 = midPt(R3, H)
    L4 = midPt(L3, R2)
    R1 = L4
    pts = bz(L1, L2, L3, L4, strict)
    pts.extend(bz(R1, R2, R3, R4, strict))
    return pts


def straight(P1, P4, strict=True) -> dotList:
    # m = diff.z / diff.x
    # z = m * (x - begin.x) + begin.z
    if close(P1, P4):
        return getUnit(P1, P4, strict)
    H = midPt(P1, P4)
    pts = straight(P1, H, strict)
    pts.extend(straight(H, P4, strict))
    return pts
