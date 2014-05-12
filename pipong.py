import pygame,sys
from pygame.locals import *

pygame.init()

SCREEN_W = 640
SCREEN_H = 480
FOREGROUND = (255,255,255)
PADDLE_W = 24
PADDLE_H = 72

SCREEN = pygame.display.set_mode((SCREEN_W,SCREEN_H))

#main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    pygame.display.update()

class Paddle(pygame.sprite.Sprite,color,width,height):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

#draw paddle rectangle
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        
    

