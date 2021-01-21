
import pygame as pg
from constant import *
from scene import *


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()

    active_scene = LogoScene()

    done = False

    while active_scene is not None:
        quit_attempt = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit_attempt = True
            active_scene.handle_event(event)

        active_scene.update()
        active_scene.render(screen)
        active_scene = active_scene.next
        if quit_attempt:
            active_scene = None
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()
