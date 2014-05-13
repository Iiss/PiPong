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

PADDLE_1_UP_KEY = pygame.K_q
PADDLE_1_DOWN_KEY =pygame.K_a 

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
# State
#
class State:
    def __init__(self):
        pass

    def on_init(self):
        pass

    def on_event(self,event):
        pass

    def on_loop(self):
        pass

    def on_render(self,surface):
        pass

    def on_cleanup(self):
        pass

#
# State Manager
#
class StateManager(object):

    _currentState = None

    class __metaclass__(type):

        @property
        def currentState(cls):
            return cls._currentState

        @currentState.setter
        def currentState(cls,value):
            
            if value != cls._currentState:
                if cls._currentState != None:
                    cls._currentState.on_cleanup()
                    
                cls._currentState = value

#
# Test state 1
#
class TestState1(State):

    def __init__(self):
        State.__init__(self)

    def on_render(self,surface):
        surface.fill((255,0,0))


#
# Test state 2
#
class TestState2(State):

    def __init__(self):
        State.__init__(self)

    def on_render(self,surface):
        surface.fill((0,255,0))
   
#
# Test state 3
#
class TestState3(State):

    def __init__(self):
        State.__init__(self)
        
    def on_render(self,surface):
        surface.fill((0,0,255))

STATES=[TestState1(),TestState2(),TestState3()]

#
# Game State
#
class GameState(State):
    def __init__(self):
        pass

    def on_init(self):
        pass

    def on_event(self,event):
        pass

    def on_loop(self):
        pass

    def on_render(self,surface):
        #draw background
        
        pass

    def on_cleanup(self):
        pass
    
#
# Main Apllication Class
#
class App:

    def __init__(self):
        self._runnting = True
        self._display_surf = None
        self.size = SCREEN_W,SCREEN_H

        self._curStateIndex=0

    def on_init(self):
        pygame.init()
        
        self._display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption("PiPong")

        self._running = True

    def on_event(self,event):
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._running = False

        if StateManager.currentState != None:
            StateManager.currentState.on_event(event)
        

    def on_loop(self):
        if StateManager.currentState != None:
            StateManager.currentState.on_loop()

    def on_render(self):
        if StateManager.currentState != None:
            StateManager.currentState.on_render(self._display_surf)

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

    StateManager.currentState = GameState()



#### temp ####
##        paddle=Paddle(FOREGROUND,PADDLE_W,PADDLE_H)
##        self._testGroup = pygame.sprite.Group()
##        self._testGroup.add(paddle)
#### temp end ####
        
    

