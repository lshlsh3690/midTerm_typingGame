import pygame #파이 게임 모듈 임포트

pygame.init() #파이 게임 초기화
Screen_height = 750     #스크린 너비
Screen_width = 1200     #스크린 높이
screen = pygame.display.set_mode((Screen_width, Screen_height)) #화면 크기 설정
clock = pygame.time.Clock() 

Image1 = pygame.image.load('image/startbtn.png')      #시작 버튼 이미지 생성
StartImage = pygame.transform.scale(Image1, (400, 150)) #이미지 크기 조절
Image2 = pygame.image.load('image/startimg.jpg')
StartBackGroundImage = pygame.transform.scale(Image2, (Screen_width, Screen_height))
pygame.display.set_caption('Typing Game')                 #게임창 타이틀 설정

validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
shiftDown = False
#버튼 클래스
class Button:
    def __init__(self, img, x, y, width, height, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        screen.blit(img,(x,y))
        if x + width > mouse[0] > x and y + height > mouse[1] > y:
            print('mouse btn is clicked')
            if action != None:
                time.sleep(1)
                action()

# class TextBox(pygame.sprite.Sprite):
#   def __init__(self):
#     pygame.sprite.Sprite.__init__(self)
#     self.text = ""
#     self.font = pygame.font.Font(None, 50)
#     self.image = self.font.render("Enter your name", False, [0, 0, 0])
#     self.rect = self.image.get_rect()
#   def add_chr(self, char):
#     global shiftDown
#     if char in validChars and not shiftDown:
#         self.text += char
#     elif char in validChars and shiftDown:
#         self.text += shiftChars[validChars.index(char)]
#     self.update()
#   def update(self):
#     old_rect_pos = self.rect.center
#     self.image = self.font.render(self.text, False, [0, 0, 0])
#     self.rect = self.image.get_rect()
#     self.rect.center = old_rect_pos
#     print(self.text)

# textBox = TextBox()

userText = ''
base_font = pygame.font.Font(None,32)
input_rect = pygame.Rect(Screen_width/2-150, Screen_height/3*1,250,32)
color = pygame.Color(255,255,255)
 
#변수
while True: #게임 루프
    screen.blit(StartBackGroundImage, (0,0))
    if userText == '':
        Textsurface = base_font.render('Enter the your name', True, (0,0,0))
    else:
        Textsurface = base_font.render(userText, True, (0,0,0))
    
    pygame.draw.rect(screen,color,input_rect)    
    screen.blit(Textsurface, input_rect)

    input_rect.w = max(100,Textsurface.get_width()+10)
    #변수 업데이트

    event = pygame.event.poll() #이트 처리
    #if event.type == pygame.QUIT:
    #    break
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit() 
        if e.type == pygame.KEYUP:
            if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                shiftDown = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_BACKSPACE:
                userText = userText[:-1]
                print(userText)
            else:
                userText += e.unicode
                print(userText)
            # textBox.add_chr(pygame.key.name(e.key))
            # if e.key == pygame.K_SPACE:
            #     textBox.text += " "
            #     textBox.update()
            # elif e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
            #     shiftDown = True
            # if e.key == pygame.K_BACKSPACE:
            #     textBox.text = textBox.text[:-1]
            #     textBox.update()
            # if e.key == pygame.K_RETURN:
            #     if len(textBox.text) > 0:
            #         print (textBox.text)
            #         pygame.quit()
    #화면 그리기

    StartButton = Button(StartImage, Screen_width/2-200, Screen_height/3*2, 400, 150, None)
    pygame.display.update() #모든 화면 그리기 업데이트
    clock.tick(60) #30 FPS (초당 프레임 수) 를 위한 딜레이 추가, 딜레이 시간이 아닌 목표로 하는 FPS 값

pygame.quit()  