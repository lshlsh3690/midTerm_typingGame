import pygame as pg
import inputbox as ib
import sys, time, random, sqlite3
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum

BLUE = (106, 159, 181)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.Font("./resource/CookieRun_Bold.otf", size=font_size)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
            action - the gamestate change associated with this button
        """
        self.mouse_over = False

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.1, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        self.images = [default_image, highlighted_image]

        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        self.action = action

        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        """ Updates the mouse_over variable and returns the button's
            action value when clicked.
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)


class SceneBase:
    def __init__(self):
        self.next = self

    def update(self):
        pass

    def render(self, screen):
        pass

    def handle_event(self, event):
        pass

    def release(self):
        pass

    def scene_change(self, next_scene):
        self.next = next_scene


class LogoScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox(330, 100, 140, 32)
        self.start_btn = UIElement(
            center_position=(400, 400),
            font_size=30,
            bg_rgb=WHITE,
            text_rgb=BLACK,
            text="시작",
            action=GameState.NEWGAME,
        )
        self.quit_btn = UIElement(
            center_position=(400, 500),
            font_size=30,
            bg_rgb=WHITE,
            text_rgb=BLACK,
            text="종료",
            action=GameState.QUIT,
        )

    def update(self):
        self.input_box.update()
        self.buttons = [self.start_btn, self.quit_btn]

    def render(self, screen):
        self.update()
        screen.fill((255, 255, 255))
        self.input_box.render(screen)

        while True:
            mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
            screen.fill(WHITE)

            for button in self.buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
                if ui_action is not None:
                    return ui_action
                button.draw(screen)

            pygame.display.flip()

    def handle_event(self, event):
        # db에 이름 저장 부분 만들어야 함
        if self.input_box.handle_event(event):
            pass

class StageScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def update(self):
        # DB 생성
        conn = sqlite3.connect("./resource/records.db", isolation_level=None)
        cursor = conn.cursor()

        # 사운드 불러오기
        pg.mixer.init()
        correct_sound = pg.mixer.Sound("./sound/good.wav")
        wrong_sound = pg.mixer.Sound("./sound/bad.wav")

        class GameStart:
            def __init__(self, user):
                self.user = user

            # 유저 입장 알림
            def user_info(self):
                print("User: {}님이 입장하였습니다.\n".format(self.user))

        words = []  # 영단어 리스트 (1000개 로드)

        n = 1  # 게임 시도 횟수
        cor_cnt = 0  # 정답 개수
        try:
            word_f = open('./resource/word.txt', 'r')  # 문제 txt 파일 로드
        except IOError:
            print("파일이 없습니다!! 게임을 진행할 수 없습니다!!")
        else:
            for c in word_f:
                words.append(c.strip())
            word_f.close()

        # 파일을 잘못 불러오거나 빈 파일이면 종료
        if words is []:
            sys.exit()

        user_name = input("Ready? Input Your name>> ")  # Enter Game Start!
        user = GameStart(user_name)  #### GameStart의 user객체 생성
        user.user_info()  #### user 입장 알림 메서드 호출

        start = time.time()  # Start Time

        while n <= 5:
            random.shuffle(words)  # 단어 리스트 뒤섞기
            q = random.choice(words)  # 뒤섞인 단어 리스트에서 랜덤으로 하나 선택

            print("{}번 문제".format(n), q)  # 문제 표시

            x = input("타이핑하세요>> ")  # 타이핑 입력

            if str(q).strip() == str(x).strip():  # (공백 제거한) 입력 확인
                pg.mixer.Sound.play(correct_sound)  # 정답 사운드 재생
                print(">>Passed!\n")
                cor_cnt += 1  # 정답 개수 카운트
            else:
                pg.mixer.Sound.play(wrong_sound)  # 오답 사운드 재생
                print("Wrong!")

            n += 1  # 다음 문제 전환

        end = time.time()  # 끝나는 시간 체크
        et = end - start  # 총 게임 시간 환산

        print('--------------')
        print()
        print("\n집계중...\n")
        time.sleep(1)

        et = format(et, ".3f")  # 시간을 소수 셋째자리까지 출력

        if cor_cnt >= 3:  # 3개 이상 합격
            print("결과 : 합격")
        else:
            print("불합격")

        self.scene_change(GameOver())

    def render(self, screen):
        screen.fill((0, 0, 0))

    def handle_event(self, event):
        pass

    def release(self):
        pass


class GameOver(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def update(self):
        pass

    def render(self, screen):
        print('Game over')
        self.scene_change(None)

    def handle_event(self, event):
        pass

    def release(self):
        pass

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1

