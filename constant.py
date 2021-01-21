import pygame as pg

# 스크린 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# 박스 크기
BOX_WIDTH = 140
BOX_HEIGHT = 32

# 목숨이 떨어지는 지점
DEAD_LINE = SCREEN_HEIGHT - 80

# TEXT 컬러 및 폰트
pg.init()
TEXT_COLOR = pg.Color('lightskyblue3')
TEXT_FONT = pg.font.Font(None, BOX_HEIGHT)
