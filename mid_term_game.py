# 타이핑 게임 (오전분반 중간고사)
# 사운드 사용 및 DB연동

import random, time, sys

# 사운드 출력, 데이터베이스, 시간 관련 필요 모듈
import pygame
import sqlite3
import datetime

# DB 생성
conn = sqlite3.connect("./resource/records.db", isolation_level=None)
cursor = conn.cursor()

# 사운드 불러오기
pygame.init()
pygame.mixer.init()
correct_sound = pygame.mixer.Sound("./sound/good.wav")
wrong_sound = pygame.mixer.Sound("./sound/bad.wav")

# 테이블 생성 (AUTOINCREMENT - 자동으로 1씩 증가)
cursor.execute("CREATE TABLE IF NOT EXISTS records (" +\
    "id INTEGER PRIMARY KEY AUTOINCREMENT, " +\
    "cor_cnt INTEGER, " +\
    "record TEXT, " +\
    "regdate TEXT)")

'''AUTOINCREMENT : 삽입할 때 insert해주지 않아도, 저절로 1씩 증가 또는 지정한 수로 증가\
    cor_cnt:정답 개수, record : 결과 '''
'''실행 했을 때 에러 발생하면 안됨. 데이터베이스 생성됐는지 확인'''

############################# 추가 코드 ############################
# GameStart 클래스 생성
class GameStart:
    def __init__(self, user):
        self.user=user
    
    # 유저 입장 알림
    def user_info(self):
        print("User: {}님이 입장하였습니다.\n".format(self.user))
#####################################################################3

words = []                                                      # 영단어 리스트 (1000개 로드)

n = 1                                                           # 게임 시도 횟수
cor_cnt = 0                                                     # 정답 개수
try:
    word_f=open('./resource/word.txt', 'r') # 문제 txt 파일 로드
except IOError:
    print("파일이 없습니다!! 게임을 진행할 수 없습니다!!")
else:
    for c in word_f:
        words.append(c.strip())
    word_f.close()

# 파일을 잘못 불러오거나 빈 파일이면 종료
if words is []:
    sys.exit()

user_name=input("Ready? Input Your name>> ")             # Enter Game Start! 
user=GameStart(user_name)                     #### GameStart의 user객체 생성
user.user_info()                              #### user 입장 알림 메서드 호출

start = time.time()                          # Start Time

while n <= 5:  
    random.shuffle(words)                                       # 단어 리스트 뒤섞기
    q = random.choice(words)                                    # 뒤섞인 단어 리스트에서 랜덤으로 하나 선택

    print("{}번 문제".format(n), q)                               # 문제 표시
    
    x = input("타이핑하세요>> ")                                    # 타이핑 입력

    if str(q).strip() == str(x).strip():                        # (공백 제거한) 입력 확인
        pygame.mixer.Sound.play(correct_sound)                  # 정답 사운드 재생
        print(">>Passed!\n")
        cor_cnt += 1                                            # 정답 개수 카운트
    else:
        pygame.mixer.Sound.play(wrong_sound)                    # 오답 사운드 재생
        print("Wrong!")
    
    n += 1                                                      # 다음 문제 전환

end = time.time()                                               # 끝나는 시간 체크
et = end - start                                                # 총 게임 시간 환산

print('--------------')
print()
print("\n집계중...\n")
time.sleep(1)

et = format(et, ".3f")                                          # 시간을 소수 셋째자리까지 출력

if cor_cnt >= 3:                             # 3개 이상 합격
    print("결과 : 합격")
else:
    print("불합격")

######### 결과 기록 DB 삽입
'''data삽입 전에 먼저 기록테이블 구조 열어보기'''
cursor.execute(
    "INSERT INTO records('cor_cnt', 'record', 'regdate') VALUES (?, ?, ?)",
    (
        cor_cnt, et, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
)
'''ID는 오토 인크리먼트이므로 입력안해줘도 자동으로 db에서 연속된 숫자형으로 넣어줌'''
'''strftime('%Y-%m-%d %H:%M:%S') : 포맷 변환'''

'''게임 실행해서 db기록되는지 확인'''
######### 접속 해제
conn.close()

# 수행 시간 출력
print("게임 시간 :", et, "초", "정답 개수 : {}".format(cor_cnt))

play()