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
