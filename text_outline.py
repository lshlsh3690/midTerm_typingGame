import pygame as pg

# 텍스트의 외곽선 그리기 (default = 2픽셀)
def outline_text(text, font, color, x, y, screen):
    render_x = [0, -1, -2, -1, 0, 1, 2, 1]
    render_y = [2, 1, 0, -1, -2, -1, 0, 1]
    for i in range(8):
        outline_word = font.render(text, True, color)
        screen.blit(outline_word, (x + render_x[i], y + render_y[i]))

