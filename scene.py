import pygame as pg
import inputbox as ib
import sys, time, random, sqlite3, word, datetime
from constant import *


class SceneBase:
    def __init__(self):
        self.next = self
        # DB 생성
        self.conn = sqlite3.connect("./resource/records.db", isolation_level=None)
        self.cursor = self.conn.cursor()
        # 테이블 생성 (AUTOINCREMENT - 자동으로 1씩 증가)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS records (" + \
                            "id INTEGER PRIMARY KEY AUTOINCREMENT," + \
                            "name TEXT , " + \
                            "life_time FLOAT, " + \
                            "score INTEGER, " + \
                            "regdate TEXT)")

    def update(self):
        pass

    def render(self, screen):
        pass

    def handle_event(self, event):
        pass

    def scene_change(self, next_scene):
        self.next = next_scene


class LogoScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.box_color = pg.Color('lightskyblue3')
        self.name_box = ib.InputBox((SCREEN_WIDTH - BOX_WIDTH) // 2, SCREEN_HEIGHT // 2, BOX_WIDTH, BOX_HEIGHT)

    def update(self):
        self.name_box.update()

    def render(self, screen):
        screen.fill('white')
        name_text = TEXT_FONT.render('name', True, TEXT_COLOR)
        screen.blit(name_text, (self.name_box.rect.x - 70, self.name_box.rect.y + 5))
        self.name_box.render(screen)

    def handle_event(self, event):
        if self.name_box.handle_event(event):
            self.cursor.execute("INSERT INTO records(name) VALUES (?)", (self.name_box.text,))
            self.scene_change(StageScene())


class StageScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox((SCREEN_WIDTH - BOX_WIDTH) // 2, SCREEN_HEIGHT - 100, BOX_WIDTH, BOX_HEIGHT)
        self.cor_text = TEXT_FONT.render('', True, TEXT_COLOR)
        self.time_text = TEXT_FONT.render('', True, TEXT_COLOR)
        self.heart = 3
        self.life_time = 0
        # 사운드 불러오기
        pg.mixer.init()
        self.correct_sound = pg.mixer.Sound("./sound/good.wav")
        self.wrong_sound = pg.mixer.Sound("./sound/bad.wav")

        # 영단어 리스트 (1000개 로드)
        self.words = []
        try:
            word_f = open('./resource/word.txt', 'r')  # 문제 txt 파일 로드
        except IOError:
            print("파일이 없습니다!! 게임을 진행할 수 없습니다!!")
        else:
            for c in word_f:
                self.words.append(c.strip())
            word_f.close()
        # 파일을 잘못 불러오거나 빈 파일이면 종료
        if self.words is []:
            sys.exit()
        random.shuffle(self.words)  # 단어 리스트 뒤섞기
        self.start = time.time()  # Start Time
        self.end = 0
        self.rain_words = []
        self.zen_time = time.time()
        self.score = 0

    def update(self):
        self.end = time.time()
        self.life_time = self.end - self.start  # 총 게임 시간 환산
        self.zen_words()
        self.input_box.update()
        for i in self.rain_words:
            i.update()
            if i.y > DEAD_LINE:
                self.rain_words.remove(i)
                pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                self.cor_text = TEXT_FONT.render('Wrong!', True, TEXT_COLOR)
                self.heart -= 1

        if self.heart <= 0:
            idx = self.cursor.execute('SELECT max(id) FROM records')
            max_id = idx.fetchone()[0]
            self.cursor.execute(
                "Update records "
                "Set life_time = ?, score = ?, regdate = ? "
                "WHERE id = ?",
                (
                    self.life_time, self.score, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), max_id
                )
            )
            # strftime('%Y-%m-%d %H:%M:%S') : 포맷 변환

            # 게임 실행해서 db기록되는지 확인
            ######### 접속 해제
            self.conn.close()

            self.scene_change(GameOver())

    def render(self, screen):
        screen.fill('black')
        self.input_box.render(screen)
        self.ui_render(screen)
        screen.blit(self.cor_text, (self.input_box.rect.x, self.input_box.rect.y - 50))
        for i in self.rain_words:
            i.render(screen)

    def handle_event(self, event):
        self.input_box.handle_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            for i in self.rain_words:
                if str(self.input_box.text).strip() == str(i.text).strip():
                    pg.mixer.Sound.play(self.correct_sound)  # 정답 사운드 재생
                    self.cor_text = TEXT_FONT.render('Passed!', True, TEXT_COLOR)
                    self.score += 20 * len(str(self.input_box.text).strip())
                    self.rain_words.remove(i)
                    break
                if i == self.rain_words[-1]:
                    pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                    self.cor_text = TEXT_FONT.render('Wrong!', True, TEXT_COLOR)
                    self.heart -= 1

            self.input_box.text = ""

    def ui_render(self, screen):
        time_text = TEXT_FONT.render('time: ' + format(self.life_time, '.3f'), True, TEXT_COLOR)
        score_text = TEXT_FONT.render('score: ' + str(self.score), True, TEXT_COLOR)
        heart_text = TEXT_FONT.render('heart: ' + str(self.heart), True, TEXT_COLOR)
        screen.blit(time_text, (260, 50))
        screen.blit(score_text, (260, 80))
        screen.blit(heart_text, (260, 110))

    def zen_words(self):
        if self.zen_time + 1 < time.time():
            self.zen_time = time.time()
            self.rain_words.append(word.Word(random.choice(self.words), SCREEN_WIDTH, SCREEN_HEIGHT))


class GameOver(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.color = pg.Color('red')
        self.font = pg.font.Font(None, 100)
        self.end_text = self.font.render('GameEnd', True, self.color)

    def update(self):
        pass

    def render(self, screen):
        screen.fill('black')
        screen.blit(self.end_text, (200, 100))

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.scene_change(None)