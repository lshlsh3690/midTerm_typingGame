import datetime

import pygame as pg
import inputbox as ib
import sys, time, random, sqlite3


class SceneBase:
    def __init__(self):
        self.next = self
        self.color = pg.Color('lightskyblue3')
        self.font = pg.font.Font(None, 32)
        self.cor_cnt = 0  # 정답 개수
        self.record = 0
        # DB 생성
        self.conn = sqlite3.connect("./resource/records.db", isolation_level=None)
        self.cursor = self.conn.cursor()
        # 테이블 생성 (AUTOINCREMENT - 자동으로 1씩 증가)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS records (" + \
                            "name TEXT PRIMARY KEY, " + \
                            "cor_cnt INTEGER, " + \
                            "record TEXT, " + \
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
        self.name_box = ib.InputBox(380, 380, 140, 40)
        self.background = pg.image.load("./image/title.png")

    def update(self):
        self.name_box.update()

    def render(self, screen):
        screen.fill((255, 255, 255))
        
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
        # db에 이름 저장 부분 만들어야 함
        if self.name_box.handle_event(event):
            self.scene_change(StageScene(self.name_box.text))


class StageScene(SceneBase):
    def __init__(self, name_str):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox(400, 700, 140, 32)
        self.typing_box = ib.InputBox(400, 100, 140, 32)
        self.cor_text = self.font.render('', True, self.color)
        self.time_text = self.font.render('', True, self.color)
        self.name_str = name_str
        # 사운드 불러오기
        pg.mixer.init()
        self.correct_sound = pg.mixer.Sound("./sound/good.wav")
        self.wrong_sound = pg.mixer.Sound("./sound/bad.wav")

        self.n = 0  # 게임 시도 횟수

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

    def update(self):
        self.input_box.update()
        self.typing_box.update()

        if self.n < 5:
            self.typing_box = ib.InputBox(400, 100, 140, 32, self.words[self.n])  # 뒤섞인 단어 리스트에서 랜덤으로 하나 선택

        else:
            if self.cor_cnt >= 3:  # 3개 이상 합격
                print("결과 : 합격")
            else:
                print("불합격")
            ######### 결과 기록 DB 삽입
            '''data삽입 전에 먼저 기록테이블 구조 열어보기'''
            self.cursor.execute(
                "INSERT INTO records('name', 'cor_cnt', 'record', 'regdate') VALUES (?, ?, ?, ?)",
                (
                    self.name_str, self.cor_cnt, self.record, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                )
            )
            '''ID는 오토 인크리먼트이므로 입력안해줘도 자동으로 db에서 연속된 숫자형으로 넣어줌'''
            '''strftime('%Y-%m-%d %H:%M:%S') : 포맷 변환'''

            '''게임 실행해서 db기록되는지 확인'''
            ######### 접속 해제
            self.conn.close()
            self.scene_change(GameOver())

    def render(self, screen):
        screen.fill((255, 255, 0))
        self.input_box.render(screen)
        self.typing_box.render(screen)
        self.timer_render(screen)
        screen.blit(self.cor_text, (400, 600))

    def handle_event(self, event):
        if self.input_box.handle_event(event):
            if str(self.words[self.n]).strip() == str(self.input_box.text).strip():  # (공백 제거한) 입력 확인
                pg.mixer.Sound.play(self.correct_sound)  # 정답 사운드 재생
                self.cor_text = self.font.render('Passed!', True, self.color)
                self.cor_cnt += 1  # 정답 개수 카운트
            else:
                pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                self.cor_text = self.font.render('Wrong!', True, self.color)
            self.input_box.text = ""
            self.n += 1

    def timer_render(self, screen):
        end = time.time()  # 끝나는 시간 체크
        self.record = end - self.start  # 총 게임 시간 환산
        self.time_text = self.font.render('score: ' + format(self.record, '.3f'), True, self.color)
        screen.blit(self.time_text, (260, 50))


class GameOver(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.color = pg.Color('red')
        self.font = pg.font.Font(None, 100)
        self.end_text = self.font.render('GameEnd', True, self.color)

    def update(self):
        pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.end_text, (200, 100))

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.scene_change(None)
