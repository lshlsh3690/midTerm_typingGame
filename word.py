import random, time
from constant import *


class Word:
    def __init__(self, word):
        self.text = word
        self.word_surface = TEXT_FONT.render(self.text, True, 'white')
        # 텍스트가 잘릴 경우를 대비해 스크린크기에 100픽셀 떨어진곳 까지만 범위를 설정
        self.x = random.randrange(0, SCREEN_WIDTH - 100)
        self.y = 0
        self.speed = 1.5 * random.uniform(1, 1.5)    # speed를 각각 랜덤으로 설정

    def update(self):
        # deadline 보다 위에 있을 시 speed 만큼 내려감
        if self.y < DEAD_LINE:
            self.y += self.speed

    def render(self, screen):
        screen.blit(self.word_surface, (self.x, self.y))