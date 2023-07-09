from .painter import Painter
from .system import System


MAIN_MENU = "main_menu"
UP = "up"
DOWN = "down"
ENTER = "enter"


class Game:
    def __init__(self, w, h, u, preview_num, fps=None):
        if w < 4:
            w = 4
        self.painter = Painter(w, h, u)
        self.system = System(w, h, preview_num)
        self.fps = fps