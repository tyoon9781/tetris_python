from typing import List


CW = "cw"
RCW = "rcw"
I = "I"
O = "O"
S = "S"
Z = "Z"
L = "L"
J = "J"
T = "T"


class Pos:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def add(self, pos):
        if isinstance(pos, tuple):
            self.x += pos[0]
            self.y += pos[1]
        elif isinstance(pos, Pos):
            self.x += pos.x
            self.y += pos.y
        elif isinstance(pos, (int, float)):
            self.x += pos
            self.y += pos

    def sub(self, pos):
        if isinstance(pos, tuple):
            self.x -= pos[0]
            self.y -= pos[1]
        elif isinstance(pos, Pos):
            self.x -= pos.x
            self.y -= pos.y
        elif isinstance(pos, (int, float)):
            self.x -= pos
            self.y -= pos

    def __add__(self, pos):
        if isinstance(pos, tuple):
            return Pos(self.x + pos[0], self.y + pos[1])
        elif isinstance(pos, Pos):
            return Pos(self.x + pos.x, self.y + pos.y)
        elif isinstance(pos, (int, float)):
            return Pos(self.x + pos, self.y + pos)
    
    def __sub__(self, pos):
        if isinstance(pos, tuple):
            return Pos(self.x - pos[0], self.y - pos[1])
        elif isinstance(pos, Pos):
            return Pos(self.x - pos.x, self.y - pos.y)
        elif isinstance(pos, (int, float)):
            return Pos(self.x - pos, self.y - pos)
        
    @property   
    def tuple(self):
        return (self.x, self.y)
    

class Mino:
    def __init__(self, name, blocks: List[Pos], center: Pos, y_offset: float=0):
        self.name = name
        self.blocks = blocks
        self.center = center
        self.rotation_status = 0  ## 0 -> 1 -> 2 -> 3 -> 0. rotate clockwise makes + 1
        self.y_offset = y_offset