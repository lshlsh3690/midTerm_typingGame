import pygame as pg
from scene import *


def main():
    pg.init()
    screen = pg.display.set_mode((800, 800))
    clock = pg.time.Clock()

    active_scene = LogoScene()

    done = False

    while active_scene is not None:
        for event in pg.event.get():
            quit_attempt = False
            if event.type == pg.QUIT:
                quit_attempt = True
            active_scene.handle_event(event)

            if quit_attempt:
                active_scene = None

        active_scene.update()
        active_scene.render(screen)
        active_scene = active_scene.next

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()
