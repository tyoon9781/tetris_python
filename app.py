import pygame as pg
import tetris


def game_handler(game):
    """
    Key map
    move mino   : ← →
    soft drop   : ↓
    hard drop   : space
    rotation    : z, x
    hold        : L shift
    reset       : r
    quit        : esc
    """
    ## KEY IN
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                game.system.try_move_left()
            elif event.key == pg.K_RIGHT:
                game.system.try_move_right()
            elif event.key == pg.K_DOWN:
                game.system.turn_on_sdf()
                game.system.try_soft_drop()
            elif event.key == pg.K_z:
                game.system.try_rotate_rcw()
            elif event.key == pg.K_x:
                game.system.try_rotate_cw()
            elif event.key == pg.K_LSHIFT:
                game.system.hold()
            elif event.key == pg.K_r:
                game.system.init()
            elif event.key == pg.K_SPACE:
                game.system.hard_drop()
            elif event.key == pg.K_ESCAPE:
                return False
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                game.system.turn_off_auto_move_left()
            elif event.key == pg.K_RIGHT:
                game.system.turn_off_auto_move_right()
            elif event.key == pg.K_DOWN:
                game.system.turn_off_sdf()

    ## STATUS
    if game.system.is_game_over():
        return False

    return True


def main():
    ## MACRO
    O_POINT = (0, 0)
    X, Y = 0, 1     ## for only pygame shape list
    MAX_FPS = 1000  ## max
    FONT_ANTIALIASING = True

    ## tetris configuration
    W, H = 10, 20
    TILE_SIZE = 40
    SCREEN_MARGIN = 20
    TILE_PREVIEW_COUNT = 5

    ## resolution    
    screen_margin = SCREEN_MARGIN
    top_margin = bot_margin = left_margin = right_margin = 4 * SCREEN_MARGIN

    ## area
    hold_area = (5 * TILE_SIZE, 3 * TILE_SIZE)
    info_area = (5 * TILE_SIZE, 10 * TILE_SIZE)
    play_area = (W * TILE_SIZE, H * TILE_SIZE)
    preview_area = (5 * TILE_SIZE, 3 * TILE_SIZE * TILE_PREVIEW_COUNT)
    _main_x_size = left_margin + hold_area[X] + screen_margin + play_area[X] + screen_margin + preview_area[X] + right_margin
    _main_y_size = top_margin + play_area[Y] + bot_margin
    main_area = (_main_x_size, _main_y_size)

    ## game init
    pg.init()
    game = tetris.Game(W, H, TILE_SIZE, TILE_PREVIEW_COUNT, MAX_FPS)

    ## screen
    main_screen = pg.display.set_mode(main_area)
    background_screen = pg.Surface(main_area)
    hold_screen = pg.Surface(hold_area)
    info_screen = pg.Surface(info_area)
    play_screen = pg.Surface(play_area)
    preview_screen = pg.Surface(preview_area)
    
    ## clock
    clock = pg.time.Clock()

    ## font
    fps_font = pg.font.SysFont("Arial", 32, bold=True)
    FPS_POS = (5, 5)
    info_font = pg.font.SysFont("Arial", 20, bold=True)

    ## game start
    game.system.init()
    application_running = True
    while application_running:
        clock.tick(game.fps)
        fps = clock.get_fps()

        ## draw screen
        main_screen.blit(background_screen, O_POINT)
        main_screen.blit(hold_screen, (left_margin, top_margin))
        main_screen.blit(info_screen, (left_margin, top_margin + hold_area[Y] + screen_margin))
        main_screen.blit(play_screen, (left_margin + hold_area[X] + screen_margin, top_margin))
        main_screen.blit(preview_screen, (left_margin + hold_area[X] + screen_margin + play_area[X] + screen_margin, top_margin))
        main_screen.blit(fps_font.render(str(int(fps)), FONT_ANTIALIASING, pg.Color("YELLOW")), FPS_POS)

        background_screen.fill(pg.Color("gray20"))
        hold_screen.fill(pg.Color("BLACK"))
        play_screen.fill(pg.Color("BLACK"))
        preview_screen.fill(pg.Color("BLACK"))

        ## draw info
        info_screen.fill(pg.Color("BLACK"))
        if game.system.combo_count > 0:
            info_screen.blit(info_font.render(str(f"Combo : {game.system.combo_count}"), 1, pg.Color("GRAY")), (screen_margin, screen_margin))
        
        pps_minutes = int(game.system.spend_second)//60
        pps_seconds = game.system.spend_second - pps_minutes*60
        info_screen.blit(info_font.render(f"Time : {pps_minutes:d}:{pps_seconds:06.3f}", 1, pg.Color("GRAY")), (screen_margin, screen_margin*3))
        info_screen.blit(info_font.render(f"Pieces : {game.system.used_mino_count}", 1, pg.Color("GRAY")), (screen_margin, screen_margin*5))

        pieces_per_seconds = game.system.used_mino_count/game.system.spend_second if game.system.spend_second > 0 else 0
        info_screen.blit(info_font.render(f"PPS : {pieces_per_seconds:.3f}", 1, pg.Color("GRAY")), (screen_margin, screen_margin*7))
        info_screen.blit(info_font.render(f"Lines : {game.system.cleaned_line}", 1, pg.Color("GRAY")), (screen_margin, screen_margin*9))

        ## game handler
        game.system.frame_check(fps)
        next_state = game_handler(game)

        if next_state is False:
            application_running = False
            break
        
        ## painter
        game.painter.draw_ghost_mino(play_screen, game.system.get_ghost_mino())
        game.painter.draw_current_mino(play_screen, game.system.get_current_mino())
        game.painter.draw_hold_mino(hold_screen, game.system.get_hold_mino())
        game.painter.draw_preview_mino_list(preview_screen, game.system.get_preview_mino_list())
        game.painter.draw_field(play_screen, game.system.get_draw_field())
        game.painter.draw_grid(play_screen)

        ## pygame display update
        pg.display.flip()


if __name__ == '__main__':
    main()