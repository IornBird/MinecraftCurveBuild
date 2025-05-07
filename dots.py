import math

rad = lambda d: d * math.pi / 180
deg = lambda r: r * 180 / math.pi
sinD = lambda x: math.sin(rad(x))
cosD = lambda x: math.cos(rad(x))


class Dot:
    def __init__(self, x: float, z: float):
        self.x = x
        self.z = z

    # -self
    def __neg__(self):
        return Dot(-self.x, -self.z)

    # self + other
    def __add__(self, other):
        return Dot(self.x + other.x, self.z + other.z)

    # self - other
    def __sub__(self, other):
        return Dot(self.x - other.x, self.z - other.z)

    # self * val
    def __mul__(self, val: float):
        return Dot(self.x * val, self.z * val)

    # self / val
    def __truediv__(self, val: float):
        return Dot(self.x / val, self.z / val)

    # self == other
    def __eq__(self, other):
        if isinstance(other, tuple | list):
            if len(other) == 2:
                return (self.x == other[0]) and (self.z == other[1])
            return TypeError
        return (self.x == other.x) and (self.z == other.z)

    def round(self):
        return Dot(round(self.x), round(self.z))

    def moveFor(self, deg, dist):
        """
        value of deg (same as in Minecraft):
            z+: 0, x+: -90
        point shot from (0, 0) with deg by L:
            L *　(-sin(deg), cos(deg))
        """
        # x = self.x - sinD(deg) * dist
        # z = self.z + cosD(deg) * dist
        # return Dot(x, z)
        return self + dotFromDeg(deg, dist)

    def getDeg(self):
        return deg(math.atan2(-self.x, self.z))

    def dot(self, other):
        return self.x * other.x + self.z * other.z

    def cross(self, other):
        """
        assume v1 and v2 are vector where y == 0
        returns y of v1 x v2; positive iff v2 on the left of v1
        """
        return self.z * other.x - other.z * self.x

    def __repr__(self):
        """For debugging, return a string representation of the dot."""
        return f"({self.x}, {self.z})"


def dotFromDeg(deg, dist):
    return Dot(- sinD(deg) * dist, cosD(deg) * dist)


def midPt(p1: Dot, p2: Dot):
    return (p1 + p2) / 2


def close(p1: Dot, p2: Dot):
    p1, p2 = p1.round(), p2.round()
    diff = p1 - p2
    return (-1 <= diff.x <= 1) and (-1 <= diff.z <= 1)


# def changedDir(p1: Dot, p2: Dot):
#     diffMax = 1e-12
#     return not (-diffMax < p1.cross(p2) < diffMax)


def changedDir(p1: Dot, p2: Dot):
    if p1 == (0, 0) or p2 == (0, 0):  # vector (0, 0) can be any direction, assume same
        return False
    diffMax = 0.01
    d1, d2 = p1.getDeg(), p2.getDeg()
    theta = (d2 - d1 + 180) % 360.0 - 180
    return not (-diffMax < theta < diffMax)


class dotList:
    class Node:
        def __init__(self, dot):
            self.data = dot
            self.next = None

        def __repr__(self):
            return f"[{self.data} at {hex(id(self))}]"

    def __init__(self, dot):
        node = self.Node(dot)
        self.head = node
        self.tail = node  # Keep track of the tail for O(1) append
        self.length = 1   # Keep track of length if needed

    def append(self, dot):
        """Add an element to the tail in O(1)."""
        new_node = self.Node(dot)
        self.tail.next = new_node
        self.tail = new_node
        self.length += 1

    def extend(self, other):
        """Link another dotList object to the tail in O(1)."""
        if other.head:
            self.tail.next = other.head
            self.tail = other.tail
            self.length += other.length

    def toInt(self):
        """Apply `round` to all elements in one pass."""
        current = self.head
        while current:
            current.data = current.data.round()
            current = current.next
        return self

    def getOffset(self):
        """Generate a new dotList with element-wise differences in one pass."""
        if not self.head or not self.head.next:
            return None  # Return None for empty or single-element list

        current = self.head
        new_list = None
        prev_data = current.data
        current = current.next
        buf = Dot(0, 0)

        while current:
            offset = current.data - prev_data  # Compute offset
            if changedDir(buf, offset):  # if offset != Dot(0, 0):
                if new_list is None:
                    new_list = dotList(buf)  # Create new list with first offset
                else:
                    new_list.append(buf)  # Append subsequent offsets
                buf = Dot(0, 0)
            buf += offset
            prev_data = current.data
            current = current.next
        if buf != (0, 0):
            if new_list is None:
                new_list = dotList(buf)  # Create new list with first offset
            else:
                new_list.append(buf)  # Append subsequent offsets

        return new_list

    def toList(self):
        ans = []
        ptr = self.head
        while ptr:
            ans.append(ptr.data)
            ptr = ptr.next
        return ans

    def toScalarList(self):
        ans = []
        ptr = self.head
        while ptr:
            ans.append((ptr.data.x, ptr.data.z))
            ptr = ptr.next
        return ans

    def cutDist(self, n: int):
        """
        Returns where to place if distance of each is n
        the list must be "offset"
        """
        if not self.head or not self.head.next:
            return None  # Return None for empty or single-element list

        current = self.head
        new_list = None
        current = current.next
        buf = Dot(0, 0)
        v = 0

        while current:
            if v >= n:
                if new_list is None:
                    new_list = dotList(buf)  # Create new list with first offset
                else:
                    new_list.append(buf)  # Append subsequent offsets
                buf = Dot(0, 0)
                v -= n
            v += current.dot(current)
            buf += current
            current = current.next
        if buf != (0, 0):
            if new_list is None:
                new_list = dotList(buf)  # Create new list with first offset
            else:
                new_list.append(buf)  # Append subsequent offsets

        return new_list

    def __repr__(self):
        """For debugging, return a string representation of the list."""
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        return " -> ".join(elements)

if __name__ == '__main__':
    # Creating a list with tuples
    L = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 1), (0, 0)]
    L = [Dot(*c) for c in L]
    for i in range(len(L) - 1):
        print(f"{L[i]}, {L[i+1]}: {changedDir(L[i], L[i+1])}")
        # print(f"{args}: {Dot(*args).getDeg()}")
