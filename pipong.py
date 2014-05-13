import pygame,sys
from pygame.locals import *

class Paddle(pygame.sprite.Sprite):

    def __init__(self,color,width,height):
        pygame.sprite.Sprite.__init__(self)

        #draw paddle rectangle
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect=self.image.get_rect()

pygame.init()

SCREEN_W = 640
SCREEN_H = 480
FOREGROUND = (255,255,255)
PADDLE_W = 24
PADDLE_H = 72

SCREEN = pygame.display.set_mode((SCREEN_W,SCREEN_H))

paddle=Paddle(FOREGROUND,PADDLE_W,PADDLE_H)




testGroup = pygame.sprite.Group()
testGroup.add(paddle)
testGroup.x=300

#main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    testGroup.draw(SCREEN)
    pygame.display.update()



        
    

