import pygame,sys
from pygame.locals import *

pygame.init()

SCREEN_W = 640
SCREEN_H = 480

SCREEN = pygame.display.set_mode((SCREEN_W,SCREEN_H))

#main loop
while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()


    

