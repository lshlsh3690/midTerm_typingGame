import inputbox as ib
import sys, time, random, sqlite3, word, datetime
from constant import *
from text_outline import outline_text

# 현재 사용자 이름을 저장하는 글로벌 변수
global current_name
current_name = ""

# 씬들의 기초가 되는 클래스
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
        # 텍스트 박스 초기화
        self.name_box = ib.InputBox(380, 380, 250, 40, 10)
        # 백그라운드 이미지 불러오기
        self.background = pg.image.load("./image/title.png")

    def update(self):
        self.name_box.update()  # 이름 입력시 name_box 내 text 필드에 저장됨

    def render(self, screen):
        # 타이틀 화면 초기화(흰색)
        screen.fill((255, 255, 255))
        # 타이틀 배경화면으로 화면 채우기
        screen.blit(self.background, (0, 0))
        # 이름 박스 렌더링
        self.name_box.render(screen)

    def handle_event(self, event):
        # enter 키가 눌린 경우 실행
        if self.name_box.handle_event(event):
            # 인게임에 표시될 이름 저장
            self.name = self.name_box.text
            global current_name
            current_name = self.name
            # db에 이름 삽입 후 스테이지 씬으로 전환
            self.cursor.execute("INSERT INTO records(name) VALUES (?)", (self.name_box.text,))
            self.scene_change(StageScene())


# 스테이지 씬 - 게임이 진행되는 곳
class StageScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.input_box = ib.InputBox(260, 719, 282, 34) # 텍스트 입력 창
        self.color = pg.Color('lightskyblue3')
        self.font = pg.font.Font(None, 32)
        self.cor_text = self.font.render('', True, self.color) # 정답/오답
        self.time_text = self.font.render('', True, self.color) # 시간
        self.background = pg.image.load("./image/ingame.png")
        self.heart = 3  # 목숨
        self.life_time = 0  # 게임 진행 시간
        # 사운드 불러오기
        pg.mixer.init()
        self.correct_sound = pg.mixer.Sound("./sound/good.wav")
        self.wrong_sound = pg.mixer.Sound("./sound/bad.wav")
        # 라이프 이미지 불러와서 x좌표와 y좌표 정보(딕셔너리)를 담은 리스트 생성
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
        self.end = 0  # end Time
        self.rain_words = []  # word 클래스 리스트
        self.zen_time = time.time()  # 단어가 떨어지는 시간 차
        self.score = 0  # 점수

    def update(self):
        # 총 게임 시간 환산
        self.end = time.time()
        self.life_time = self.end - self.start  
        self.zen_words()  # 단어들을 생성
        self.input_box.update()
        # word 리스트에서 각각의 인스턴스에서 y 좌표 변경
        for i in self.rain_words:
            i.update()
            # 일정 높이 이하로 단어가 떨어질시 오답 처리
            if i.y > DEAD_LINE:
                self.rain_words.remove(i)
                pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                # 하트 1 감소, 감소된 하트만큼 회색 하트로 교체
                self.heart -= 1
                self.heart_container[self.heart]['img'] = self.heart_gray
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
                    min(9999.999, self.life_time), # 10000초가 넘어갈 경우 9999.999초로 고정  
                    min(999999, self.score),  # 1000000점 이상일 경우 999999로 점수 고정
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
                    max_id
                )
            )
            self.conn.close()
            self.scene_change(GameOver())

    def render(self, screen):
        # 본 게임 배경화면 렌더링
        screen.fill('black')
        screen.blit(self.background, (0, 0))
        # 텍스트 입력 박스 렌더링
        self.input_box.render(screen)
        # UI 렌더링
        self.ui_render(screen)
        # 각각의 단어 렌더링
        for i in self.rain_words:
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
                    self.score += 20 * len(str(self.input_box.text).strip())    # 스코어 = 단어 길이*20
                    self.rain_words.remove(i)
                    break
                # 맨 마지막 까지 검색해서 안나온 경우 ==> 오타
                if i == self.rain_words[-1]:
                    pg.mixer.Sound.play(self.wrong_sound)  # 오답 사운드 재생
                    # 하트 1 감소, 감소된 하트만큼 회색 하트로 교체
                    self.heart -= 1
                    self.heart_container[self.heart]['img'] = self.heart_gray

            self.input_box.text = ""    # 텍스트 박스의 내용을 지움

    # 시간, 스코어, 목숨을 출력
    def ui_render(self, screen):
        # 정보 텍스트 여백 설정
        info_text_margin = 3
        global current_name

        # 정보 텍스트(시간, 점수), 이름 텍스트 폰트 설정 후 렌더링
        info_font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 18)
        name_font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 18)
        time_text = info_font.render(format(self.life_time, '.3f'), True, self.highlighted_color)
        score_text = info_font.render(str(self.score), True, self.highlighted_color)
        name_text = name_font.render(current_name, True, self.highlighted_color)

        # UI 구성요소를 화면에 출력
        screen.blit(time_text, (97+info_text_margin, 720+info_text_margin))
        screen.blit(score_text, (97+info_text_margin, 759+info_text_margin))
        screen.blit(name_text, (358+info_text_margin, 109+info_text_margin))

        # 라이프(하트) 이미지 출력
        for heart in self.heart_container:
            screen.blit(heart['img'], (heart['x'], heart['y']))

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

        # 결과 배경화면 불러오기
        self.background = pg.image.load("./image/result.jpg")

        # 랭킹 폰트 설정
        self.rank_font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 17)
        # 1-이름 2-생존시간 3-점수
        self.myscore_surface = []
        self.myscore_str = ['You', ]
        self.myscore_str.append(self.mydata[1])
        self.myscore_str.append('%.3f' % self.mydata[2])
        self.myscore_str.append(str(self.mydata[3]))  

        for string in self.myscore_str:
            self.myscore_surface.append(self.rank_font.render(string, True, 'white'))

        
        # 랭커 정보 조회
        self.rankers = self.cursor.execute('SELECT name, life_time, score FROM records order by score DESC').fetchall()
        self.ranker_surface_list = []
        self.ranker_str = []
        # 1위부터 10위까지 표시
        for i in range(0, 10):
            if i < self.rankers.__len__():
                # 0-번호, 1-이름, 2-시간, 3-점수
                self.ranker_str_individual = []
                self.ranker_surface_individual = []
                self.ranker_str_individual.append((str(i + 1)))
                self.ranker_str_individual.append(self.rankers[i][0])
                self.ranker_str_individual.append('%.3f' % self.rankers[i][1])
                self.ranker_str_individual.append('%d' % self.rankers[i][2])
                self.ranker_surface_individual.append(self.rank_font.render((str(i + 1)), True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render(self.rankers[i][0], True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render('%.3f' % self.rankers[i][1], True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render('%d' % self.rankers[i][2], True, 'white'))
            else:   # 만일 db에 저장된 데이터가 10개 미만인 경우 빈 곳을 NULL로 지정
                self.ranker_str_individual = []
                self.ranker_surface_individual = []
                self.ranker_str_individual.append((str(i + 1)))
                self.ranker_str_individual.append('NULL')
                self.ranker_str_individual.append('NULL')
                self.ranker_str_individual.append('NULL')
                self.ranker_surface_individual.append(self.rank_font.render((str(i + 1)), True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render('NULL', True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render('NULL', True, 'white'))
                self.ranker_surface_individual.append(self.rank_font.render('NULL', True, 'white'))
            self.ranker_surface_list.append(self.ranker_surface_individual)
            self.ranker_str.append(self.ranker_str_individual)

    def render(self, screen):
        # 결과 배경화면으로 화면 채우기
        screen.fill('black')
        screen.blit(self.background, (0, 0))

        # 자신의 스코어 출력
        field_x_placement = [172, 260, 430, 558]
        record_y_placement = 305
        screen.fill((180, 180, 180))
        for i, surface in enumerate(self.myscore_surface):
            outline_surface = self.rank_font.render(self.myscore_str[i], True, 'dodgerblue2')
            outline_text(outline_surface, field_x_placement[i], record_y_placement, screen)
            screen.blit(surface, (field_x_placement[i], record_y_placement))

        # 1위부터 10위까지 y좌표에 차이를 두어 출력 - 사람이 10명 미만이면 10명 미만만 출력
        record_y_placement = 338
        for i in range(0, min(len(self.ranker_surface_list), 10)):
            for j, surface in enumerate(self.ranker_surface_list[i]):
                outline_surface = self.rank_font.render(self.ranker_str[i][j], True, 'dodgerblue2')
                outline_text(outline_surface, field_x_placement[j], record_y_placement, screen)
                screen.blit(surface, (field_x_placement[j], record_y_placement))
            record_y_placement += 22

    # 결과 화면 이벤트 처리 부분
    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            # ESC - 게임 종료
            if event.key == pg.K_ESCAPE:
                self.scene_change(None)
            # R - 게임 재시작
            if event.key == pg.K_r:
                self.scene_change(LogoScene())
