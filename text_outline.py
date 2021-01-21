import pygame as pg

# 텍스트의 외곽선 그리기 (default = 3)
def outline_text(text, font, color, x, y, screen):
    render_x = [0, -2, -3, -2, 0, 2, 3, 2]
    render_y = [3, 2, 0, -2, -3, -2, 0, 2]
    for i in range(8):
        outline_word = font.render(text, True, color)
        screen.blit(outline_word, (x + render_x[i], y + render_y[i]))

