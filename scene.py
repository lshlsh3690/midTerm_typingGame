import inputbox as ib
import sys, time, random, sqlite3, word, datetime
from constant import *


# 씬들의 기초가 되는 클래스
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

    # 화면에 그리는 메소드
    def render(self, screen):
        pass

    # event 처리 메소드
    def handle_event(self, event):
        pass

    # 씬 변환 메소드
    def scene_change(self, next_scene):
        self.next = next_scene


# 맨 처음 로고 화면-이름 입력을 하면 스테이지 씬으로 전환
class LogoScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        # 이름 입력 박스 생성 & 위치 및 색상 결정
        self.box_color = pg.Color('lightskyblue3')
        self.name_box = ib.InputBox((SCREEN_WIDTH - BOX_WIDTH) // 2, SCREEN_HEIGHT // 2, BOX_WIDTH, BOX_HEIGHT)

    def update(self):
        self.name_box.update()  # 이름 입력시 name_box 내 text 필드에 저장됨

    def render(self, screen):
        screen.fill('white')  # 하얀색 배경
        name_surface = TEXT_FONT.render('name', True, TEXT_COLOR)  # 출력할 메세지, 안티얼라이어스, 색상을 지정
        screen.blit(name_surface, (self.name_box.rect.x - 70, self.name_box.rect.y + 5))  # 지정한 메세지를 name_box 왼쪽에 출력
        self.name_box.render(screen)  # 이름 입력 박스 출력

    def handle_event(self, event):
        # enter 키가 눌린 경우 실행
        if self.name_box.handle_event(event):
            # db에 이름 삽입 후 스테이지 씬으로 전환
            self.cursor.execute("INSERT INTO records(name) VALUES (?)", (self.name_box.text,))
            self.scene_change(StageScene())


# 스테이지 씬 - 게임이 진행되는 곳
class StageScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox((SCREEN_WIDTH - BOX_WIDTH) // 2, SCREEN_HEIGHT - 100, BOX_WIDTH,
                                     BOX_HEIGHT)  # 텍스트 입력 창
        self.cor_surface = TEXT_FONT.render('', True, TEXT_COLOR)  # 정답/오답
        self.time_surface = TEXT_FONT.render('', True, TEXT_COLOR)  # 시간
        self.heart = 3  # 목숨
        self.life_time = 0  # 게임 진행 시간
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
        self.end = 0  # end Time
        self.rain_words = []  # word 클래스 리스트
        self.zen_time = time.time()  # 단어가 떨어지는 시간 차
        self.score = 0  # 점수

    def update(self):
        self.end = time.time()
        self.life_time = self.end - self.start  # 총 게임 시간 환산
        self.zen_words()  # 단어들을 생성
        self.input_box.update()
        # word 리스트에서 각각의 word 인스턴스에서 y 좌표 변경
        # 일정 높이 이하로 단어가 떨어질시 오답 처리
        for i in self.rain_words:
            i.update()
            if i.y > DEAD_LINE:
                self.rain_words.remove(i)
                pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                self.cor_surface = TEXT_FONT.render('Wrong!', True, TEXT_COLOR)  # 오답 시 Wrong 표시
                self.heart -= 1

        # 목숨이 떨어지면 이때까지의 기록을 db에 저장
        # GameOver 씬으로 전환
        if self.heart <= 0:
            # 이름을 입력한 id를 불러옴
            idx = self.cursor.execute('SELECT max(id) FROM records')
            max_id = idx.fetchone()[0]
            # 해당 id에 기록 저장
            self.cursor.execute(
                "Update records "
                "Set life_time = ?, score = ?, regdate = ? "
                "WHERE id = ?",
                (
                    self.life_time, self.score, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), max_id
                )
            )
            self.conn.close()
            self.scene_change(GameOver())

    def render(self, screen):
        screen.fill('black')
        self.input_box.render(screen)
        self.ui_render(screen)
        screen.blit(self.cor_surface, (self.input_box.rect.x, self.input_box.rect.y - 50))  # 텍스트 입력 창 위에 정답/오답 표시
        for i in self.rain_words:   # 각각의 단어 렌더링
            i.render(screen)

    def handle_event(self, event):
        self.input_box.handle_event(event)
        # 단어 입력 후 ENTER 키가 눌릴 시
        if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            # 화면에 생성한 단어 리스트와 입력한 단어를 비교
            for i in self.rain_words:
                # 정답 시 score를 올리고 해당 단어를 리스트에서 제거
                if str(self.input_box.text).strip() == str(i.text).strip():
                    pg.mixer.Sound.play(self.correct_sound)  # 정답 사운드 재생
                    self.cor_surface = TEXT_FONT.render('Passed!', True, TEXT_COLOR)    # 정답시 Passed 표시
                    self.score += 20 * len(str(self.input_box.text).strip())    # 스코어 = 단어 길이*20
                    self.rain_words.remove(i)
                    break
                # 맨 마지막 까지 검색해서 안나온 경우 ==> 오타
                if i == self.rain_words[-1]:
                    pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                    self.cor_surface = TEXT_FONT.render('Wrong!', True, TEXT_COLOR)  # 오답시 Wrong 표시
                    self.heart -= 1

            self.input_box.text = ""    # 텍스트 박스의 내용을 지움

    # 시간, 스코어, 목숨을 출력
    def ui_render(self, screen):
        time_surface = TEXT_FONT.render('time: ' + format(self.life_time, '.3f'), True, TEXT_COLOR)
        score_surface = TEXT_FONT.render('score: ' + str(self.score), True, TEXT_COLOR)
        heart_surface = TEXT_FONT.render('heart: ' + str(self.heart), True, TEXT_COLOR)
        screen.blit(time_surface, (260, 50))
        screen.blit(score_surface, (260, 80))
        screen.blit(heart_surface, (260, 110))

    # 랜덤하게 시간 차를 두고 단어가 떨어지게 해줌
    def zen_words(self):
        if self.zen_time + random.uniform(1, 1.5) < time.time():  # 1~1.5초 사이 랜덤한 시간이 지나면
            self.zen_time = time.time() # 젠 시간 초기화
            self.rain_words.append(word.Word(random.choice(self.words)))    # 랜덤한 단어를 추가


# 게임오버씬-본인 점수, 랭킹을 10위까지 표시함
class GameOver(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        # 저장한 본인 데이터 조회
        self.mydata = self.cursor.execute('SELECT max(id), name, life_time, score FROM records').fetchone()

        # GameOver 메세지 설정
        self.end_font = pg.font.Font('./font/PottaOne-Regular.ttf', 100)
        self.end_surface = self.end_font.render('GameOver', True, 'black')
        # 랭킹 메세지 설정
        self.rank_font = pg.font.Font('./font/PottaOne-Regular.ttf', 32)
        self.rank_str = 'name    time    score'
        self.rank_surface = self.rank_font.render(self.rank_str, True, 'black')
        # 1-이름 2-생존시간 3-점수
        self.myscore_str = 'Your     ' + self.mydata[1] + '  ' + format(self.mydata[2], '.3f') + '    ' + str(
            self.mydata[3])
        self.myscore_surface = self.rank_font.render(self.myscore_str, True, 'black')
        # 랭커 정보 조회
        self.rankers = self.cursor.execute('SELECT name, life_time, score FROM records order by score DESC').fetchall()
        self.ranker_surface_list = []
        self.ranker_str = ""
        # 1위부터 10위까지
        for i in range(0, 10):
            if i < self.rankers.__len__():
                # 0-이름 1-생존시간 2-점수
                self.ranker_str = ('%3s'% str(i + 1) + '%10s' % self.rankers[i][0] + '%10.3f' % self.rankers[i][1] +'%5d' % self.rankers[i][2])
            else:   # 만일 db에 저장된 데이터가 10개 미만인 경우 빈 곳을 NULL로 지정
                self.ranker_str = (str(i + 1) + '    NULL    NULL    NULL')
            self.ranker_surface_list.append(self.rank_font.render(self.ranker_str, True, 'black'))

    def render(self, screen):
        screen.fill((180, 180, 180))
        screen.blit(self.end_surface, (145, 50))
        screen.blit(self.rank_surface, (170, 150))
        screen.blit(self.myscore_surface, (100, 200))
        # 1위부터 10위까지 y좌표에 차이를 두어 출력
        for i in range(0, 10):
            screen.blit(self.ranker_surface_list[i], (150, 200 + (i + 1) * 30))

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            # ESC - 게임 종료
            if event.key == pg.K_ESCAPE:
                self.scene_change(None)
            # R - 게임 재시작
            if event.key == pg.K_r:
                self.scene_change(LogoScene())
