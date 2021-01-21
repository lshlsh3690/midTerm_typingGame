from constant import *
from scene import *


def main():
    pg.init()   # 파이게임 초기화
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()

    active_scene = LogoScene()  # 첫 화면 = 로고씬

    while active_scene is not None:
        quit_attempt = False
        # 이벤트 처리
        for event in pg.event.get():
            # 종료 이벤트 시 종료
            if event.type == pg.QUIT:
                quit_attempt = True
            # 씬내 이벤트 처리
            active_scene.handle_event(event)

        active_scene.update()   # 씬 업데이트
        active_scene.render(screen) # 씬 그리기
        # 씬 전환
        active_scene = active_scene.next
        # 종료 처리
        if quit_attempt:
            active_scene = None
        pg.display.flip()   # 화면 업데이트
        clock.tick(30)      # 30프레임


if __name__ == '__main__':
    main()
    pg.quit()
