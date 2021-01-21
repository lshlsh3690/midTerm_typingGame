import pygame as pg
import inputbox as ib
import sys, time, random, sqlite3, word, datetime
from constant import *
from text_outline import outline_text

class SceneBase:
    def __init__(self):
        self.next = self
        # 화면 구성요소 기본값 설정
        self.color = pg.Color('lightskyblue3')
        self.highlighted_color = pg.Color('dodgerblue2')
        self.font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 32)
        self.bold_font = pg.font.Font(GAME_FONT_BOLD_PATH, 32)
        self.cor_cnt = 0  # 정답 개수
        self.record = 0
        # DB 생성
        self.conn = sqlite3.connect("./resource/records.db", isolation_level=None)
        self.cursor = self.conn.cursor()
        self.name = ""
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
        next_scene.name = self.name
        self.next = next_scene


class LogoScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.name_box = ib.InputBox(380, 380, 250, 40, 10)
        self.background = pg.image.load("./image/title.png")

    def update(self):
        self.name_box.update()

    def render(self, screen):
        # 타이틀 화면 초기화(흰색)
        screen.fill((255, 255, 255))
        # 디자인된 배경화면으로 화면 채우기
        screen.blit(self.background, (0, 0))

        # 제목 추가
        # title_string = 'Typing Game'
        # title_font = pg.font.Font(None, 60)
        # title_font_size = title_font.size(title_string)
        # title_text = title_font.render(title_string, True, self.color)
        
        # name_text = self.font.render('name', True, self.color)

        # 아래 안내 문구 추가
        # info1_string = 'Type your name and press Enter key to start'
        # info1_font = pg.font.Font(None, 30)
        # info1_font_size = info1_font.size(info1_string)
        # info1_text = info1_font.render(info1_string, True, self.color)

        # info2_string = "(If the name you input exists, the game wouldn't start.)"
        # info2_font = pg.font.Font(None, 30)
        # info2_font_size = info2_font.size(info2_string)
        # info2_text = info2_font.render(info2_string, True, self.color)
        
        # name_text = self.font.render('name', True, self.color)
        
        # screen.blit(title_text, ((screen.get_width() // 2) - (title_font_size[0] // 2), 200))
        # screen.blit(name_text, (260, 405))
        # screen.blit(info1_text, ((screen.get_width() // 2) - (info1_font_size[0] // 2), 600))
        # screen.blit(info2_text, ((screen.get_width() // 2) - (info2_font_size[0] // 2), 630))
        self.name_box.render(screen)

    def handle_event(self, event):
        if self.name_box.handle_event(event):
            self.name = self.name_box.text
            self.cursor.execute("INSERT INTO records(name) VALUES (?)", (self.name_box.text,))
            self.scene_change(StageScene())


class StageScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox(260, 719, 282, 34)
        self.color = pg.Color('lightskyblue3')
        self.font = pg.font.Font(None, 32)
        self.cor_text = self.font.render('', True, self.color)
        self.time_text = self.font.render('', True, self.color)
        self.background = pg.image.load("./image/ingame.png")
        self.heart = 3
        self.life_time = 0
        # 사운드 불러오기
        pg.mixer.init()
        self.correct_sound = pg.mixer.Sound("./sound/good.wav")
        self.wrong_sound = pg.mixer.Sound("./sound/bad.wav")
        # 라이프 이미지 불러오기
        self.heart_red = pg.image.load("./image/heart_red.png")
        self.heart_gray = pg.image.load("./image/heart_gray.png")
        self.heart_container = [
            {'img': self.heart_red, 'x': 715-65-65, 'y': 721},
            {'img': self.heart_red, 'x': 715-65, 'y': 721},
            {'img': self.heart_red, 'x': 715, 'y': 721}
        ]

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
            if i.y > BOTTOM_HEIGHT:
                self.rain_words.remove(i)
                pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                self.cor_text = self.font.render('Wrong!', True, self.color)
                self.heart -= 1
                self.heart_container[self.heart]['img'] = self.heart_gray
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
        screen.fill((0, 0, 0))
        screen.blit(self.background, (0, 0))
        
        self.input_box.render(screen)
        self.ui_render(screen)
        # screen.blit(self.cor_text, (400, 600))
        for i in self.rain_words:
            i.render(screen)

    def handle_event(self, event):
        self.input_box.handle_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            for i in self.rain_words:
                if str(self.input_box.text).strip() == str(i.text).strip():
                    pg.mixer.Sound.play(self.correct_sound)  # 정답 사운드 재생
                    self.cor_text = self.font.render('Passed!', True, self.color)
                    self.score += 20 * len(str(self.input_box.text).strip())
                    self.rain_words.remove(i)
                    break
                if i == self.rain_words[-1]:
                    pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                    self.cor_text = self.font.render('Wrong!', True, self.color)
                    self.heart -= 1
                    self.heart_container[self.heart]['img'] = self.heart_gray

            self.input_box.text = ""

    def ui_render(self, screen):
        info_text_margin = 3

        info_font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 18)
        name_font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 18)
        
        time_text = info_font.render(format(self.life_time, '.3f'), True, self.highlighted_color)
        score_text = info_font.render(str(self.score), True, self.highlighted_color)
        name_text = name_font.render(self.name, True, self.highlighted_color)

        screen.blit(time_text, (97+info_text_margin, 720+info_text_margin))
        screen.blit(score_text, (97+info_text_margin, 759+info_text_margin))
        screen.blit(name_text, (358+info_text_margin, 109+info_text_margin))

        # 라이프(하트) 이미지 출력
        for heart in self.heart_container:
            screen.blit(heart['img'], (heart['x'], heart['y']))

    def zen_words(self):
        if self.zen_time + 1 < time.time():
            self.zen_time = time.time()
            self.rain_words.append(word.Word(random.choice(self.words), 670, 800))


class GameOver(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.conn = sqlite3.connect("./resource/records.db", isolation_level=None)
        self.cursor = self.conn.cursor()
        self.cursor.execute("select * from records")
        a = self.cursor.fetchall()
        print(a[len(a)-1])
        self.your_score = int(a[len(a)-1][3])
        print(self.your_score)

        self.high_score= int(self.your_score)
        
        for i in range(len(a)):
            if int(a[i][3]) > self.high_score :
                self.high_score = a[i][3]
        self.font = pg.font.Font(None, 100)
        self.font = pg.font.Font('./font/PottaOne-Regular.ttf', 100)
        self.end_text = self.font.render('GameOver', True, (0,0,0))
        self.font = pg.font.Font('./font/PottaOne-Regular.ttf', 50)
        self.yourscore = self.font.render('Your Score : '+str(self.your_score), True, (0,0,0))
        self.highscore = self.font.render('High Score : '+str(self.high_score), True, (0,0,0))
    def update(self):
        pass

    def render(self, screen):
        screen.fill((180, 180, 180))
        screen.blit(self.end_text, (145,100))
        screen.blit(self.yourscore, (130, 300))
        screen.blit(self.highscore, (130, 500))

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.scene_change(None)