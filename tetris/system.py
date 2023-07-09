from copy import deepcopy
from random import choice

from .configuration import *


class System:
    _mino_list = [
        Mino(I, [Pos(-1, 0), Pos( 0, 0), Pos( 1, 0), Pos( 2, 0)], Pos(0.5, 0.5), y_offset=-0.5),
        Mino(O, [Pos( 0,-1), Pos( 0, 0), Pos( 1, 0), Pos( 1,-1)], Pos(0.5,-0.5)),
        Mino(S, [Pos(-1,-1), Pos( 0,-1), Pos( 0, 0), Pos( 1, 0)], Pos(0.0, 0.0)),
        Mino(Z, [Pos(-1, 0), Pos( 0, 0), Pos( 0,-1), Pos( 1,-1)], Pos(0.0, 0.0)),
        Mino(L, [Pos(-1,-1), Pos(-1, 0), Pos( 0, 0), Pos( 1, 0)], Pos(0.0, 0.0)),
        Mino(J, [Pos(-1, 0), Pos( 0, 0), Pos( 1, 0), Pos( 1,-1)], Pos(0.0, 0.0)),
        Mino(T, [Pos( 0,-1), Pos( 0, 0), Pos(-1, 0), Pos( 1, 0)], Pos(0.0, 0.0)),
    ]
    _rotation_group1 = O + S + Z + L + J + T
    _rotation_group2 = I
    _rotation_table = {
        _rotation_group1: {
            CW: {
                0:[( 0, 0), (-1, 0), (-1,-1), ( 0, 2), (-1, 2)],
                1:[( 0, 0), ( 1, 0), ( 1, 1), ( 0,-2), ( 1,-2)],
                2:[( 0, 0), ( 1, 0), ( 1,-1), ( 0, 2), ( 1, 2)],
                3:[( 0, 0), (-1, 0), (-1,-1), ( 0,-2), (-1,-2)],
            },
            RCW: {
                0:[( 0, 0), ( 1, 0), ( 1,-1), ( 0, 2), ( 1, 2)],
                1:[( 0, 0), ( 1, 0), ( 1, 1), ( 0,-2), ( 1,-2)],
                2:[( 0, 0), (-1, 0), (-1,-1), ( 0, 2), (-1, 2)],
                3:[( 0, 0), (-1, 0), (-1, 1), ( 0,-2), (-1,-2)],
            }
        },
        _rotation_group2:{
            CW: {
                0:[( 0, 0), (-2, 0), ( 1, 0), (-2, 1), ( 1,-2)],
                1:[( 0, 0), (-1, 0), ( 2, 0), (-1,-2), ( 2, 1)],
                2:[( 0, 0), ( 2, 0), (-1, 0), ( 2,-1), (-1, 2)],
                3:[( 0, 0), ( 1, 0), (-2, 0), ( 1, 2), (-2,-1)],
            },
            RCW: {
                0:[( 0, 0), (-1, 0), ( 2, 0), (-1,-2), ( 2, 1)],
                1:[( 0, 0), ( 2, 0), (-1, 0), ( 2,-1), (-1, 2)],
                2:[( 0, 0), ( 1, 0), (-2, 0), ( 1, 2), (-2,-1)],
                3:[( 0, 0), (-2, 0), ( 1, 0), (-2, 1), ( 1,-2)],
            }
        }
    }


    def __init__(self, w, h, preview_num=5):
        """
        w, h : viewing field (ex : 10 * 20)
        h_padding : hidden area for stacking over viewing field. so real field is 10 * 40

        """
        self.w = w
        self.h = h
        self.h_padding = h
        self.preview_num = preview_num
        self.init()
    
    def init(self):
        self.curr_mino: Mino = None
        
        ## field
        self.field = [[False for _ in range(self.w)] for _ in range(self.h + self.h_padding)]
        self._field_new_line = [[False for _ in range(self.w)]]
        self._init_mino_pos = self._get_init_mino_pos()
        self._all_bag_cases = self._get_all_numbers_of_case(len(self._mino_list))
        self._bag, self._next_bag = choice(self._all_bag_cases), choice(self._all_bag_cases)
        
        ## fps
        self.spend_second = 0
        
        ## timeout land system
        self._timeout_land_count = 0
        self._timeout_land_limit_second = 1
        self._timeout_enable_land = False
        
        ## soft drop factor system
        self._sdf_count = 0
        self._sdf_passive_stack_speed = 1
        self._sdf_active_stack_speed = 80
        self._sdf_stack = 1
        self._sdf_limit_second = 1
               
        ## Delayed Auto Shift system
        self._r_das_count = 0
        self._r_das_limit_second = 0.15
        self._r_das_operation = False
        self._l_das_count = 0
        self._l_das_limit_second = 0.15
        self._l_das_operation = False
        
        ## Auto Repeat Rate system
        self._r_arr_count = 0
        self._r_arr_limit_second = 0.01
        self._r_arr_operation = False
        self._l_arr_count = 0
        self._l_arr_limit_second = 0.01
        self._l_arr_operation = False
        
        ## hold system
        self._curr_mino_num = False
        self._hold_mino_num = False
        self._hold_used = False
        
        ## score system
        self.used_mino_count = 0
        self.combo_count = 0
        self.cleaned_line = 0
        self._is_tspin = False
        
        self.init_next_mino()
        
    def init_next_mino(self):
        self._hold_used = False
        self.curr_mino = self._get_next_mino()
        self._set_curr_mino_init_position()
        
    def hold(self):
        if self._hold_used:
            return False
        
        self._hold_used = True
        
        if self._hold_mino_num is False:
            self._hold_mino_num = self._curr_mino_num
            self.curr_mino = self._get_next_mino()
        else:
            self._hold_mino_num, self._curr_mino_num = self._curr_mino_num, self._hold_mino_num
            self.curr_mino = self._get_mino(self._curr_mino_num)
        self._set_curr_mino_init_position()

    def frame_check(self, fps):
        if fps > 1:
            self.spend_second += 1/(fps)
            self._check_y_gravity_time(fps)
            self._check_land_time(fps)
            self._check_r_das_timer(fps)
            self._check_l_das_timer(fps)
            self._check_r_arr_timer(fps)
            self._check_l_arr_timer(fps)

    def is_game_over(self):
        for i in range(4):
            if self.field[self.h_padding][self._get_w_center() - 2 + i] is not False:
                return True
        return False

    def hard_drop(self):
        while self._is_enable_move_y():
            self._move_y()
        self._land_for_next_mino()
        
    def try_move_right(self):
        self.turn_on_auto_move_right()
        self._try_move_x(1)
    
    def try_move_left(self):
        self.turn_on_auto_move_left()
        self._try_move_x(-1)
        
    def _try_move_x(self, dx):
        if self._is_enable_move_x(dx):
            self._move_x(dx)

    def try_soft_drop(self):
        if self._is_enable_move_y():
            self._move_y()
        elif self._timeout_enable_land:
            self._land_for_next_mino()
            
    def try_rotate_rcw(self):
        self._try_rotate(RCW)
    
    def try_rotate_cw(self):
        self._try_rotate(CW)

    def _try_rotate(self, rotation):
        if self._is_enable_rotate(rotation):
            self._rotation_status_update(rotation)
            
    def turn_on_auto_move_right(self):
        self.turn_off_auto_move_right()
        self.turn_off_auto_move_left()
        self._r_das_operation = True
        
    def turn_off_auto_move_right(self):
        self._r_das_operation = False
        self._r_das_count = 0
        self._r_arr_operation = False
        self._r_arr_count = 0

    def turn_on_auto_move_left(self):
        self.turn_off_auto_move_right()
        self.turn_off_auto_move_left()
        self._l_das_operation = True
        
    def turn_off_auto_move_left(self):
        self._l_das_operation = False
        self._l_das_count = 0
        self._l_arr_operation = False
        self._l_arr_count = 0

    def turn_on_sdf(self):
        self._sdf_stack = self._sdf_active_stack_speed

    def turn_off_sdf(self):
        self._sdf_stack = self._sdf_passive_stack_speed

    def get_current_mino(self):
        send_mino = deepcopy(self.curr_mino)
        for block in send_mino.blocks:
            block.sub((0, self.h_padding))
        return send_mino

    def get_preview_mino_list(self):
        return [self._get_mino(_num) for _num in (self._bag + self._next_bag)[:self.preview_num]]

    def get_hold_mino(self):
        return self._get_mino(self._hold_mino_num)

    def get_ghost_mino(self):
        ghost_mino = deepcopy(self.curr_mino)
        count = 0
        blank_underline = True
        while blank_underline:
            for block in ghost_mino.blocks:
                next_pos_y = block.y + count + 1 
                if next_pos_y >= len(self.field) or self.field[next_pos_y][block.x] is not False:
                    blank_underline = False
                    break;
                    
            if blank_underline:
                count += 1
                
        for block in ghost_mino.blocks:
            block.y += (count)
            
        for block in ghost_mino.blocks:
            block.sub((0, self.h_padding))
            
        return ghost_mino

    def get_draw_field(self):
        return self.field[self.h_padding:]

    def _set_curr_mino_init_position(self):
        for block_pos in self.curr_mino.blocks:
            block_pos.add(self._init_mino_pos)
        self.curr_mino.center += self._init_mino_pos

    def _check_y_gravity_time(self, fps):
        self._sdf_count += self._sdf_stack
        if self._sdf_count > self._sdf_limit_second * fps:
            self.try_soft_drop()
            self._sdf_count = 0
            
    def _check_land_time(self, fps):
        self._timeout_land_count += 1
        if self._timeout_land_count >= self._timeout_land_limit_second * fps:
            self._timeout_enable_land = True
            self._timeout_land_count = 0
        
    def _check_r_arr_timer(self, fps):
        if self._r_arr_operation:
            self._r_arr_count += 1
            if self._r_arr_count > self._r_arr_limit_second * fps:
                self._try_move_x(1)
                self._r_arr_count = 0

    def _check_l_arr_timer(self, fps):
        if self._l_arr_operation:
            self._l_arr_count += 1
            if self._l_arr_count > self._l_arr_limit_second * fps:
                self._try_move_x(-1)
                self._l_arr_count = 0
        
    def _check_r_das_timer(self, fps):
        if self._r_das_operation:
            self._r_das_count += 1
            if self._r_das_count > self._r_das_limit_second * fps:
                self._r_arr_operation = True
                self._r_das_operation = False
 
    def _check_l_das_timer(self, fps):
        if self._l_das_operation:
            self._l_das_count += 1
            if self._l_das_count > self._l_das_limit_second * fps:
                self._l_arr_operation = True
                self._l_das_operation = False

    def _is_enable_rotate(self, rotated_direction=CW):
        blocks = deepcopy(self.curr_mino.blocks)
        for block in blocks:
            block.x, block.y = self._block_rotation(block, self.curr_mino.center, rotated_direction)
            
        for rotate_offset_option in self._get_rotate_offset_option_list(rotated_direction):
            _offset_blocks = deepcopy(blocks)
            if self._is_enable_rotation_offset(_offset_blocks, rotate_offset_option):
                self._rotation(rotated_direction, rotate_offset_option)
                return True
        return False

    def _get_rotate_offset_option_list(self, rotated_direction):
        group = self._rotation_group1 if self.curr_mino.name in self._rotation_group1 else self._rotation_group2
        return self._rotation_table[group][rotated_direction][self.curr_mino.rotation_status]

    def _is_enable_rotation_offset(self, blocks, rotate_offset_option):
        for block in blocks:
            block.add(rotate_offset_option)
            status1 = self._is_over_y_boundary(block)
            status2 = self._is_over_x_boundary(block)
            if status1 or status2 or self._is_field_filled(block):
                return False
        return True
    
    def _rotation_status_update(self, rotation):
        self._timeout_land_count = 0
        if rotation == CW:
            self.curr_mino.rotation_status += 1
        elif rotation == RCW:
            self.curr_mino.rotation_status -= 1
        self.curr_mino.rotation_status %= 4
        
    def _land_for_next_mino(self):
        self.used_mino_count += 1
        self._land_mino()
        _just_cleaned_line = self._try_clean_filled_line()
        self._update_combo_count(_just_cleaned_line)
        self.init_next_mino()

    def _update_combo_count(self, cleaned_line):
        if cleaned_line > 0:
            self.combo_count += 1
        else:
            self.combo_count = 0

    def _land_mino(self):
        for block in self.curr_mino.blocks:
            self.field[block.y][block.x] = self.curr_mino.name
        self._timeout_enable_land = False

    def _try_clean_filled_line(self):
        filled_idx = sorted([idx for idx, row_line in enumerate(self.field) if not False in row_line], reverse=True)
        clear_lines = len(filled_idx)
        self.cleaned_line += clear_lines
        for idx in filled_idx:
            self._clear_line(idx)
        for idx in filled_idx:
            self._add_new_line()
        return clear_lines

    def _clear_line(self, y):
        del self.field[y]

    def _add_new_line(self):
        new_field = deepcopy(self._field_new_line)
        new_field.extend(self.field)
        self.field = new_field

    def _rotation(self, rotated_direction, rotate_offset_option):
        for block in self.curr_mino.blocks:
            block.x, block.y = self._block_rotation(block, self.curr_mino.center, rotated_direction)
            block.add(rotate_offset_option)
        self.curr_mino.center += rotate_offset_option

    def _move_y(self):
        for block in self.curr_mino.blocks:
            block.y += 1
        self.curr_mino.center.y += 1
        self._timeout_enable_land = False
    
    def _move_x(self, dx):
        self._timeout_land_count = 0
        for block in self.curr_mino.blocks:
            block.x += dx
        self.curr_mino.center.x += dx
        self._timeout_enable_land = False
    
    def _is_enable_move_y(self):
        for block in deepcopy(self.curr_mino.blocks):
            block.y += 1
            if self._is_over_y_boundary(block) or self._is_field_filled(block):
                return False
        return True
        
    def _is_enable_move_x(self, dx):
        for block in deepcopy(self.curr_mino.blocks):
            block.x += dx
            if self._is_over_x_boundary(block) or self._is_field_filled(block):
                return False
        return True
    
    def _is_over_y_boundary(self, block):
        return block.y > self.h + self.h_padding - 1
    
    def _is_over_x_boundary(self, block):
        return block.x < 0 or block.x > self.w - 1

    def _get_mino(self, mino_num):
        if mino_num is False:
            return False
        return deepcopy(self._mino_list[mino_num])
        
    def _get_next_mino(self):
        if len(self._bag) == 0:
            self._bag = self._next_bag
            self._next_bag = choice(self._all_bag_cases)
        self._curr_mino_num = self._bag.pop(0)
        return deepcopy(self._mino_list[self._curr_mino_num])

    def _is_field_filled(self, block):
        if block.y < 0 or block.x < 0:
            return False
        return self.field[block.y][block.x]

    def _get_init_mino_pos(self):
        return Pos(self._get_w_center() - 1, self.h_padding)

    def _get_w_center(self):
        return self.w//2

    @staticmethod
    def _block_rotation(block: Pos, center: Pos, rotation):
        ## cos90 = 0
        sin90_y, sin90_x = block.y - center.y, block.x - center.x
        if rotation == CW:
            return round(center.x - sin90_y), round(center.y + sin90_x)
        else:   ## RCW
            return round(center.x + sin90_y), round(center.y - sin90_x)

    @staticmethod
    def _get_all_numbers_of_case(num=5):
        def _recursive_x_fill(_x, _elements):
            for i in _elements:
                x_copy = _x.copy()
                _elements_copy = _elements.copy()
                x_copy[len(_elements_copy)-1] = i
                _elements_copy.remove(i)
                if len(_elements_copy) == 0:
                    all_minos_bag_list.append(x_copy)
                else:
                    _recursive_x_fill(x_copy, _elements_copy)
        all_minos_bag_list = []
        x = [0 for _ in range(0, num)]
        elements = list(range(0, num))
        _recursive_x_fill(x, elements)
        return all_minos_bag_list