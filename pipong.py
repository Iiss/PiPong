import pygame,sys
from pygame.locals import *

#
# Global Settings
#
SCREEN_W = 640
SCREEN_H = 480
FPS = 60
FOREGROUND = (255,255,255)

MARGIN_V = 4
LINE_W = 8

PADDLE_W = 12
PADDLE_H = 56
PADDLE_MARGIN_H = 24
PADDLE_MARGIN_V = MARGIN_V+LINE_W

PADDLE_1_UP_KEY = pygame.K_q
PADDLE_1_DOWN_KEY = pygame.K_a

#
# Rectangle Sprite
#
class RectangleSprite(pygame.sprite.Sprite):

    def __init__(self,color,width,height):
        pygame.sprite.Sprite.__init__(self)

        #draw paddle rectangle
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect=self.image.get_rect()

    def move(self,x,y):
        self.rect.x = x
        self.rect.y = y
#
# Control Behavior
#
class PaddleControlBehavior:
    def __init__(self):
        self.up_key = None
        self.down_key = None

#
# Paddle
#
class Paddle(RectangleSprite):

    def __init__(self,color,width,height):
        RectangleSprite.__init__(self,color,width,height)
        self.speed = 6
        self.walls = None

    def update(self):

        direction = 0
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[PADDLE_1_UP_KEY]:
           direction -= 1

        elif keys_pressed[PADDLE_1_DOWN_KEY]:
           direction += 1
        
        dy=direction*self.speed
        
        if self.walls != None:
            collision_index = self.rect.collidelist(self.walls)

            if collision_index!=-1:
                collision_rect=self.walls[collision_index]

               

                if direction == -1:
                    dy = collision_rect.bottom-self.rect.top
                    print(collision_rect,collision_rect.bottom,self.rect.top,dy)

            
        self.rect = self.rect.move(0,dy)

        

        
                
            

      

        


#
# Wall
#
class Wall(RectangleSprite):

    def __init__(self,color,width,height):
        RectangleSprite.__init__(self,color,width,height)

#
# State
#
class State:
    def __init__(self):
        self._display_list = None

    def on_init(self):
        pass

    def on_event(self,event):
        pass

    def on_loop(self):
        pass

    def on_render(self,surface):
        if self._display_list != None:
            self._display_list.draw(surface)
            self._display_list.update()

    def on_cleanup(self):
        pass

    def add(self,obj):
        if self._display_list == None:
            self._display_list = pygame.sprite.Group()

        self._display_list.add(obj)

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
# Game State
#
class GameState(State):
    def __init__(self):
        State.__init__(self)

        self._paddle_1 = Paddle((255,0,0),PADDLE_W,PADDLE_H)
        self._paddle_1.move(PADDLE_MARGIN_H,.5*(SCREEN_H- self._paddle_1.rect.h))

        self._paddle_2 = Paddle(FOREGROUND,PADDLE_W,PADDLE_H)
        self._paddle_2.move(SCREEN_W - PADDLE_MARGIN_H - self._paddle_2.rect.w,self._paddle_1.rect.y)

        self.add(self._paddle_1)
      #  self.add(self._paddle_2)

        self._top_wall = Wall(FOREGROUND,SCREEN_W,LINE_W)
        self._bottom_wall = Wall(FOREGROUND,SCREEN_W,LINE_W)

        self._top_wall.move(0,MARGIN_V)
        self._bottom_wall.move(0,SCREEN_H-MARGIN_V-LINE_W)

        self.add(self._top_wall)
        self.add(self._bottom_wall)

        walls=[self._top_wall.rect,self._bottom_wall.rect]

        self._paddle_1.walls=walls
        
        self.bg_color=(0,0,0)

    #draw background
    def draw_bg(self,surface):
        surface.fill(self.bg_color)
        
        lasty = starty = MARGIN_V+LINE_W
        endy = SCREEN_H-MARGIN_V-LINE_W
        gap = 8

        while lasty < endy:
            pygame.draw.rect(surface,FOREGROUND,(.5*(SCREEN_W-LINE_W),lasty,LINE_W,LINE_W))
            lasty+=(LINE_W+gap)


    def on_render(self,surface):
        self.draw_bg(surface)
        State.on_render(self,surface)
                  
    
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
        self._clock = pygame.time.Clock()

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

            pygame.display.flip()
            self._clock.tick(FPS)

        self.on_cleanup()

if __name__ == "__main__":

    theApp = App()
    StateManager.currentState = GameState()
    theApp.on_execute()
        
    

