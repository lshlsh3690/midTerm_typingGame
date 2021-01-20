# -*- coding: utf-8 -*-

# pygame 모듈 임포트
import pygame


def show_title():
    # 창 초기화
    pygame.init()
    screen = pygame.display.set_mode((800, 600)) #화면 크기 설정
    clock = pygame.time.Clock() 
    while True: #게임 루프
        screen.fill((255, 255, 255)) #단색으로 채워 화면 지우기

        #변수 업데이트

        event = pygame.event.poll() #이벤트 처리
        if event.type == pygame.QUIT:
            break

        #화면 그리기
        

        pygame.display.update() #모든 화면 그리기 업데이트
        clock.tick(60) #30 FPS (초당 프레임 수) 를 위한 딜레이 추가, 딜레이 시간이 아닌 목표로 하는 FPS 값
    
    pygame.quit()    