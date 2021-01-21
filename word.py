import random, time

from text_outline import outline_text
import pygame as pg
from constant import DEAD_LINE, TOP_HEIGHT, SCREEN_WIDTH, GAME_FONT_MEDIUM_PATH

class Word:
    def __init__(self, word):
        # 텍스트 렌더링 설정
        self.font = pg.font.Font(GAME_FONT_MEDIUM_PATH, 25)
        self.text = word
        self.word = self.font.render(self.text, True, (255, 255, 255))
        # 텍스트가 잘릴 경우를 대비해 스크린크기에 10(왼쪽)~100(오른쪽)픽셀 떨어진곳 까지만 범위를 설정
        self.x = random.randrange(10, SCREEN_WIDTH - 100)
        # 단어가 생성되기 시작하는 곳 설정
        self.y = TOP_HEIGHT

        self.speed = 1.5 * random.uniform(1, 1.5)    # speed를 각각 랜덤으로 설정

    def update(self):
        # deadline 보다 위에 있을 시 speed 만큼 내려감
        if self.y < DEAD_LINE:
            self.y += self.speed

    def render(self, screen):
        # 텍스트 아웃라인 렌더링
        outline_text(self.text, self.font, pg.Color('dodgerblue2'), self.x, self.y, screen)
        # 단어 출력
        screen.blit(self.word, (self.x, self.y))

