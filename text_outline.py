import pygame as pg

# 텍스트의 외곽선 그리기 (default = 2픽셀)
# 파라미터 - 텍스트 원본, 폰트, 외곽선, xy좌표, 화면객체
def outline_text(surface, x, y, screen):
    render_x = [0, -1, -2, -1, 0, 1, 2, 1]
    render_y = [2, 1, 0, -1, -2, -1, 0, 1]
    for i in range(8):
        screen.blit(surface, (x + render_x[i], y + render_y[i]))

