import pygame,sys
from pygame.locals import *

#
# Global Settings
#
SCREEN_W = 640
SCREEN_H = 480
FOREGROUND = (255,255,255)
PADDLE_W = 24
PADDLE_H = 72

#
# Paddle
#
class Paddle(pygame.sprite.Sprite):

    def __init__(self,color,width,height):
        pygame.sprite.Sprite.__init__(self)

        #draw paddle rectangle
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect=self.image.get_rect()

        
#
# Main Apllication Class
#
class App:

    def __init__(self):
        self._runnting = True
        self._display_surf = None
        self.size = SCREEN_W,SCREEN_H

    def on_init(self):
        pygame.init()
        
        self._display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption("PiPong")

        self._running = True
        
#### temp ####
        paddle=Paddle(FOREGROUND,PADDLE_W,PADDLE_H)
        self._testGroup = pygame.sprite.Group()
        self._testGroup.add(paddle)
#### temp end ####

    def on_event(self,event):
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._testGroup.draw(self._display_surf)

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

            pygame.display.update()

        self.on_cleanup()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()




        
    

