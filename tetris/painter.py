from .configuration import *
import pygame as pg


class Painter:
    _grid_color = (40, 40, 40)
    _grid_width = 1
    _death_zone_color = (255, 64, 64)
    _ghost_color = (255, 255, 255)
    _color_map = {
        I: (54, 167, 141),
        O: (166, 166, 81),
        S: (177, 86,  90),
        Z: (143, 173, 60),
        L: (73,  94, 158),
        J: (202, 121, 65),
        T: (183, 92, 165), 
    }

    def __init__(self, w, h, u):
        self.w = w
        self.h = h
        self.u = u
        self.init()
    
    def init(self):
        self._grid_list = [pg.Rect(x*self.u, y*self.u, self.u, self.u) for x in range(self.w) for y in range(self.h)]
        self._death_zone_list = [pg.Rect((self._get_w_center()-2+i)*self.u, 0, self.u, self.u) for i in range(4)]
        self._rect_unit_printer = pg.Rect(0, 0, self.u, self.u)
    
    def draw_grid(self, screen):
        [self._draw_rect(screen, self._grid_color, grid, self._grid_width) for grid in self._grid_list]
        [self._draw_rect(screen, self._death_zone_color, death_zone, self._grid_width*2) for death_zone in self._death_zone_list]
    
    def draw_current_mino(self, screen, curr_mino: Mino):
        self._draw_mino(screen, curr_mino)
    
    def draw_ghost_mino(self, screen, ghost_mino: Mino):
        self._draw_mino(screen, ghost_mino, color=self._get_half_tone_color(self._get_mino_color(ghost_mino)))

    def draw_hold_mino(self, screen, hold_mino: Mino):
        if hold_mino is False:
            return False
        self._draw_mino(screen, hold_mino, offset=Pos(2 - hold_mino.center.x, hold_mino.y_offset + 1.5))
            
    def draw_field(self, screen, field):
        for y, row in enumerate(field):
            for x, cell in enumerate(row):
                if cell is not False:
                    self._draw_rect(screen, self._color_map[cell], self._get_rect_printer(x, y))

    def draw_preview_mino_list(self, screen, mino_list:List[Mino]):
        for i, mino in enumerate(mino_list):
            self._draw_mino(screen, mino, offset=Pos(2 - mino.center.x, i*3 + mino.y_offset + 1.5))
    
    def _draw_mino(self, screen, mino:Mino, color:tuple=None, offset:Pos=Pos(0, 0)):
        color = color if color is not None else self._get_mino_color(mino)
        for block in mino.blocks:
            self._draw_rect(screen, color, self._get_rect_printer(block.x + offset.x, block.y + offset.y))
    
    def _get_mino_color(self, mino:Mino):
        return self._color_map[mino.name]
    
    def _get_rect_printer(self, x, y):
        self._rect_unit_printer.x = round(x * self.u)
        self._rect_unit_printer.y = round(y * self.u)
        return self._rect_unit_printer
    
    def _get_w_center(self):
        return self.w//2

    @staticmethod
    def _get_half_tone_color(color:tuple):
        return (color[0]//2, color[1]//2, color[2]//2)
    
    @staticmethod
    def _draw_rect(screen, color, rect: pg.Rect, width=0):
        pg.draw.rect(screen, color, rect, width)