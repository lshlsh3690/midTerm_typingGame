import pygame as pg
from scene import *


def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()

    logo_scene = LogoScene()
    done = False
    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = logo_scene.render(screen)

        if game_state == GameState.NEWGAME:
            # game_state = play_level(screen)
            pass

        if game_state == GameState.QUIT:
            pygame.quit()
            return


if __name__ == '__main__':
    main()
    pg.quit()
