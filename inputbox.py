import pygame as pg
from hollow import textOutline

pg.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font("fonts/Gong_Gothic_OTF_Medium.otf", 30)

def get_outline(image,color=(0,0,0)):
    """Returns an outlined image of the same size.  the image argument must
    either be a convert surface with a set colorkey, or a convert_alpha
    surface. color is the color which the outline will be drawn."""
    rect = image.get_rect()
    mask = pg.mask.from_surface(image)
    outline = mask.outline()
    outline_image = pg.Surface(rect.size).convert_alpha()
    outline_image.fill((0,0,0,0))
    for point in outline:
        outline_image.set_at(point,color)
    return outline_image

class InputBox:
    def __init__(self, x, y, w, h, letter_limit=20, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.letter_limit = letter_limit
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            if self.active:
                self.color = COLOR_ACTIVE
            else:
                self.color = COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    return True
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                # 닉네임 10글자 이하 제약조건 추가
                else:
                    if len(self.text) < self.letter_limit:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(250, self.txt_surface.get_width()+10)
        self.rect.w = width

    def render(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)