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
                