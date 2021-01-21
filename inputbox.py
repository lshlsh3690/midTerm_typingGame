import pygame as pg

pg.init()   # 파이게임 초기화
# 활성화/비활성화 컬러 설정 및 폰트 설정
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False     # 박스 활성화 상태 플래그

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # 입력 박스를 user가 클릭 한 경우
            if self.rect.collidepoint(event.pos):
                # 박스 활성화
                self.active = not self.active
            else:
                self.active = False
            # 활성화 상태에 따라 박스 컬러를 바꾼다.
            if self.active:
                self.color = COLOR_ACTIVE
            else:
                self.color = COLOR_INACTIVE
        # 박스가 활성화 상태에서 키가 눌렸을 경우
        if event.type == pg.KEYDOWN:
            if self.active:
                # 엔터 키가 눌릴 경우 scene에서 이벤트 처리를 위해 True를 리턴한다.
                if event.key == pg.K_RETURN:
                    return True
                # 백스페이스가 눌린경우 텍스트를 하나 지운다.
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # 텍스트가 너무 길게 입력될 경우 박스 크기를 늘린다.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def render(self, screen):
        # 박스와 텍스트를 출력
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.color, self.rect, 2)