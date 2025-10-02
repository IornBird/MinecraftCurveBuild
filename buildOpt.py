import inspect

class Block:
    """
    It's for a Minecraft block.
    """
    def __init__(self, block, **kwargs):
        """
        example usage:
        - Block(Block&) -> get copy
        - Block('log', axis='x') -> a Minecraft block with fill state
        - Block("log[axis=x]") -> a Minecraft block with fill state
        """
        self.name = ''
        self.state = kwargs
        # Block('log', axis='x')
        if kwargs:
            self.name = block
            self.state = kwargs

        # Block(Block&)
        elif isinstance(block, Block):
            self.name = block.name
            self.state = block.state

        # Block("log[axis=x]")
        elif isinstance(block, str):
            name, kwargs = Block.analysis(block)
            self.name = name
            self.state = kwargs

        # Error
        else:
            raise TypeError(
                "Invalid argument for Block.__init__\n" + inspect.getdoc(Block.__init__)
            )
    
    def __copy__(self):
        """Copy constructor"""
        return Block(self.name, **self.state)
    
    @classmethod
    def from_string(cls, block: str):
        """Constructor that takes a string in format 'name[state1=value1,state2=value2,...]'"""
        name, state = cls.analysis(block)
        return cls(name, **state)
    
    @staticmethod
    def analysis(s: str):
        """
        Input: str like a[s1=c1, s2=c2, ...]
        Output: (a, {'s1': 'c1', 's2': 'c2'})
        """
        s = s.split('[')
        name = s[0]
        state = {}
        if len(s) == 2:
            s = s[1].strip(' ]')
            s = s.split(',')
            for c in s:
                c = c.split('=')
                if len(c) == 2:
                    state[c[0].strip()] = c[1].strip()
        return name, state

    def __repr__(self):
        ans = self.name
        opt = []
        if not self.state:
            return ans
        for c in self.state:
            opt.append(f'{c}={self.state[c]}')
        return ans + "[" + ','.join(opt) + "]"

def getInfo(s: str):
    """
    split the string into parts: name, type, default value, comment
    """
    comment = ''
    s = s.split('#')
    if len(s) == 2:
        comment = s[1].strip()
    default = ''
    s = s[0].split('=')
    if len(s) == 2:
        default = s[1].strip()
    name, type_ = '', ''
    s = s[0].split(':')
    name = s[0].strip()
    if len(s) == 2:
        type_ = s[1].strip()
    return name, type_, default, comment


def doClass(s: str):
    """
    generate a class named BuildOpt with the given attributes
    """
    s = s.split('\n')
    s = [c for c in s if c]
    p = [getInfo(c) for c in s]
    print(*p, sep='\n')
    head = "class BuildOpt:\n    def __init__(self"
    body = ''
    for i, c in enumerate(p):
        h = f', {c[0]}'
        b = f'self.{c[0]}'
        if c[1]:
            h += f': {c[1]}'
            b += f': {c[1]}'
        if c[2]:
            h += f' = {c[2]}'
        b += f' = {c[0]}'
        if c[3]:
            b += f'  # {c[3]}'
        head += h
        body += '\n' + ' ' * 8 + b
    head += '):'
    ans = head + body
    # check
    compile(ans, 'doClass', 'exec')

    return ans


if __name__ == '__main__':
    print(doClass('''
gBlock: Block = Block('quartz_block') # block_for_ground
rBlock: Block = Block('diorite')      # block_under_rail
wBlock: Block = Block('glass')        # block_wrap
wrap: bool = False
place_arrow: bool = False
place_rail: bool = False
'''))


class BuildOpt:
    def __init__(self, gBlock: Block = Block('quartz_block'), rBlock: Block = Block('diorite'),
                 wBlock: Block = Block('glass'), wrap: bool = False, place_arrow: bool = False,
                 place_rail: bool = False):
        self.gBlock: Block = gBlock  # block_for_ground
        self.rBlock: Block = rBlock  # block_under_rail
        self.wBlock: Block = wBlock  # block_wrap
        self.wrap: bool = wrap
        self.place_arrow: bool = place_arrow
        self.place_rail: bool = place_rail
