import random, time
from constant import *


class Word:
    def __init__(self, word):
        self.text = word
        self.word_surface = TEXT_FONT.render(self.text, True, 'white')
        self.x = random.randrange(50, SCREEN_WIDTH - 50)
        self.y = 0
        self.speed = 10 * random.uniform(1, 1.5)
        self.past_time = time.time()
        self.delay_time = random.uniform(0.1, 0.8)

    def update(self):
        if self.past_time + self.delay_time < time.time():
            self.past_time = time.time()

            if self.y < DEAD_LINE:
                self.y += self.speed

    def render(self, screen):
        screen.blit(self.word_surface, (self.x, self.y))