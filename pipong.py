import pygame,sys
from pygame.locals import *
from math import *
from random import *

#
# Global Settings
#
SCREEN_W = 800
SCREEN_H = 600
FPS = 360
FOREGROUND = (255,255,255)
BACKGROUND = (0,0,0)
TEST = (255,0,0)

MARGIN_V = 0
LINE_W = 8

PADDLE_W = 12
PADDLE_H = 56
PADDLE_MARGIN_H = 24
PADDLE_MARGIN_V = MARGIN_V+LINE_W

PADDLE_1_UP_KEY = pygame.K_q
PADDLE_1_DOWN_KEY = pygame.K_a

PADDLE_2_UP_KEY = pygame.K_p
PADDLE_2_DOWN_KEY = pygame.K_l

pygame.font.init()
font = pygame.font.Font("assets/visitor1.ttf",96)


#
# Collision detection
#
COLLISIONS={}
def collide(sprite,group_name):
    group = COLLISIONS[group_name]

    if group != None:
        collision_index = sprite.rect.collidelist(group)
        return collision_index!=-1
            
    return false
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

    def __init__(self,color,width,height,controls):
        RectangleSprite.__init__(self,color,width,height)
        self.speed = 1
        self.walls = None
        self.controls = controls
        self.bounce_direction=1

    def update(self):

       
        direction = 0
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[self.controls.up_key]:
            direction -= 1

        if keys_pressed[self.controls.down_key]:
           direction += 1
        
        dy=self.speed*direction

        self.rect.top += dy
        

        move=self.rect.move(0,dy)

        walls=COLLISIONS['walls']
        
        if walls != None:
            collision_index = move.collidelist(walls)

            if collision_index!=-1:
                collision_rect=walls[collision_index]

                if direction == -1:
                    self.rect.top = collision_rect.bottom

                if direction == 1:
                    self.rect.bottom = collision_rect.top

#
# Ball
#
class Ball(RectangleSprite):
    def __init__(self,color,width):
        RectangleSprite.__init__(self,color,width,width)
        self.speed = 1
        self.speedX=0;
        self.speedY=0;
        self.lastX=0
        self.lastY=0;
        self.respawn()
        
    def update(self):
        walls=COLLISIONS['walls']
        paddles=COLLISIONS['paddles']
        
        if walls != None:
            collision_index = self.rect.collidelist(walls)

            if collision_index!=-1:
                self.speedY*=-1
                wall_sfx.play()


        if paddles != None:
            collision_list = pygame.sprite.spritecollide(self,paddles,False)
            if len(collision_list)>0:
                paddle=collision_list[0]

                if self.speedX*paddle.bounce_direction<0:
                    self.update_speed_vector(self.rect.x,self.rect.y,paddle.bounce_direction < 0)
                    paddle_sfx.play()
        
        self.lastX+=self.speedX
        self.lastY+=self.speedY
        self.rect.x = self.lastX
        self.rect.y = self.lastY
        
    def respawn(self):
        midX=.5*(SCREEN_W-self.rect.width)
        midY=.5*(SCREEN_H-self.rect.height)

        self.update_speed_vector(midX,midY,random()>.5)

    def update_speed_vector(self,x,y,go_left):
        self.lastX=x
        self.lastY=y

        self.move(self.lastX,self.lastY)

        angle = random()*pi/2-pi/4

        self.speedX=cos(angle)*self.speed
        self.speedY=sin(angle)*self.speed

        if go_left and self.speedX>0:
            self.speedX*=-1
        
#
# Wall
#
class Wall(RectangleSprite):

    def __init__(self,color,width,height):
        RectangleSprite.__init__(self,color,width,height)
#
# Counter
#
class Counter(pygame.sprite.Sprite):
    def __init__(self):
        super(Counter,self).__init__()
        self.set_value_to(99)
        
    def set_value_to(self,value):
        self.image = font.render(str(value),False,FOREGROUND)
        self.rect=self.image.get_rect()


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
            self._display_list.update()
            self._display_list.draw(surface)
            

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
# Base state
#
class AbstractState(State):
    def __init__(self):
        State.__init__(self)
        self.bg=pygame.Surface([SCREEN_W,SCREEN_H])

        bg_color=(0,0,0)
        self.bg.fill(bg_color)
        
        lasty = starty = MARGIN_V+LINE_W
        endy = SCREEN_H-MARGIN_V-LINE_W
        gap = 8
        
        while lasty < endy:
            pygame.draw.rect(self.bg,FOREGROUND,(.5*(SCREEN_W-LINE_W),lasty,LINE_W,LINE_W))
            lasty+=(LINE_W+gap)

        
        self._top_wall = Wall(FOREGROUND,SCREEN_W,LINE_W)
        self._bottom_wall = Wall(FOREGROUND,SCREEN_W,LINE_W)

        self._top_wall.move(0,MARGIN_V)
        self._bottom_wall.move(0,SCREEN_H-MARGIN_V-LINE_W)

        self.need_bg=True

    def on_render(self,surface):
        if self.need_bg:
            self.need_bg=False
            self.bg.blit(self._top_wall.image,[self._top_wall.rect.x,self._top_wall.rect.y])
            self.bg.blit(self._bottom_wall.image,[self._bottom_wall.rect.x,self._bottom_wall.rect.y])
            surface.blit(self.bg,[0,0])
            pygame.display.update()
    
        State.on_render(self,surface)
#
# Title State
#
class TitleState(AbstractState):
    def __init__(self):
        AbstractState.__init__(self)
        
    def on_event(self,event):
        AbstractState.on_event(self,event)
        keys_pressed = pygame.key.get_pressed()


        if keys_pressed[PADDLE_1_UP_KEY] and keys_pressed[PADDLE_1_DOWN_KEY] or keys_pressed[PADDLE_2_UP_KEY] and keys_pressed[PADDLE_2_DOWN_KEY]:
            StateManager.currentState=GameState()
            
#
# Game State
#
class GameState(AbstractState):
    def __init__(self):
        AbstractState.__init__(self)

        controls1 = PaddleControlBehavior()
        controls1.up_key = PADDLE_1_UP_KEY
        controls1.down_key = PADDLE_1_DOWN_KEY
        
        controls2 = PaddleControlBehavior()
        controls2.up_key = PADDLE_2_UP_KEY
        controls2.down_key = PADDLE_2_DOWN_KEY
    
        self._paddle_1 = Paddle(FOREGROUND,PADDLE_W,PADDLE_H,controls1)
        self._paddle_1.move(PADDLE_MARGIN_H,.5*(SCREEN_H- self._paddle_1.rect.h))

        self._paddle_2 = Paddle(FOREGROUND,PADDLE_W,PADDLE_H,controls2)
        self._paddle_2.move(SCREEN_W - PADDLE_MARGIN_H - self._paddle_2.rect.w,self._paddle_1.rect.y)
        self._paddle_2.bounce_direction=-1

        self.add(self._paddle_1)
        self.add(self._paddle_2)

        self._ball = Ball(FOREGROUND,12)

        self.add(self._ball)

        COLLISIONS['walls']=[self._top_wall.rect,self._bottom_wall.rect]
        COLLISIONS['paddles']=[self._paddle_1,self._paddle_2]

        self._score1=0
        self._score2=0

        self._counter1=Counter()
        self._counter1.rect.x = .5*SCREEN_W-40-self._counter1.rect.w
        self._counter1.rect.y = 16
        self.add(self._counter1);
    
        self._counter2=Counter()
        self._counter2.rect.x = .5*SCREEN_W+50
        self._counter2.rect.y = 16
        self.add(self._counter2);
        
        ### counters rendering fix part ###
        self._counter1_updaterect= pygame.Rect(.5*SCREEN_W-156,self._counter1.rect.y,116,88)
        self._counter2_updaterect= pygame.Rect(.5*SCREEN_W+50,self._counter2.rect.y,116,88)
        ### end fix part ###
        
    def render_counter(self,count):
        return font.render(str(count),False,FOREGROUND)


    def on_render(self,surface):

        update_areas=[]

        for sp in self._display_list.sprites():
            if sp.rect:
                update_areas.append(pygame.Rect(sp.rect.x,sp.rect.y,sp.rect.w,sp.rect.h))
                surface.blit(self.bg,[sp.rect.x,sp.rect.y],sp.rect)

        surface.blit(self.bg,[self._counter1_updaterect.x,self._counter1_updaterect.y],self._counter1_updaterect)
        surface.blit(self.bg,[self._counter2_updaterect.x,self._counter2_updaterect.y],self._counter2_updaterect)

        AbstractState.on_render(self,surface)

        if self._ball.rect.right<0:
            self._score2+=1;

            if self._score2>99:
                self._score2=0
        
            self._counter2.set_value_to(self._score2)
            self._counter2.rect.x = .5*SCREEN_W+50
            self._counter2.rect.y = 16
            self._ball.respawn()
            
        if self._ball.rect.left>SCREEN_W:
            self._score1+=1;
            
            if self._score1>99:
                self._score1=0

            self._counter1.set_value_to(self._score1)
            self._counter1.rect.x = .5*SCREEN_W-40-self._counter1.rect.w
            self._counter1.rect.y = 16
            self._ball.respawn()

        for sp in self._display_list.sprites():
            if sp.rect:
                update_areas.append(sp.rect)
                
        ### counters rendering fix part ###
        update_areas.append(self._counter1_updaterect)
        update_areas.append(self._counter2_updaterect)
        ### end fix part ###
        
        pygame.display.update(update_areas)

        
#
# Main Apllication Class
#
class App:

    def __init__(self,width,height):
        self._runnting = True
        self._display_surf = None
        self.size = width,height

        self._curStateIndex=0

    def on_init(self):
        pygame.init()
        
        self._display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption("PiPong")

        self._running = True
        self._clock = pygame.time.Clock()

        try:
            global wall_sfx
            wall_sfx = pygame.mixer.Sound('assets/wall_blip.wav')  #load sound
            global paddle_sfx
            paddle_sfx = pygame.mixer.Sound('assets/paddle_blip.wav')  #load sound
        except:
            raise UserWarning, "could not load or play soundfiles in 'data' folder :-("

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

            self._clock.tick(FPS)

        self.on_cleanup()

if __name__ == "__main__":

    pygame.mixer.pre_init(44100, -16, 2, 2048)

    theApp = App(SCREEN_W,SCREEN_H)

    StateManager.currentState = TitleState()
    theApp.on_execute()
        
    

