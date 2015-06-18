import pygame,sys
from pygame.locals import *
from math import *
from random import *
from time import sleep
#
# Global Settings
#
SCREEN_W = 800
SCREEN_H = 600
FPS = 180
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

REPLAY_KEY = pygame.K_r

pygame.font.init()
font = pygame.font.Font("assets/visitor1.ttf",96)
title_font = pygame.font.Font("assets/visitor1.ttf",64)


#
# GPIO integration
#

GPIO_READY=False

gpio_P1_up=27
gpio_P1_down=22
gpio_P2_up=2
gpio_P2_down=4
gpio_Replay=17

try:
    import RPi.GPIO as gpio
    GPIO_READY=True
    
except ImportError:
    print("GPIO is not available")

if GPIO_READY:
    gpio.setmode(gpio.BCM)
    gpio.setup(gpio_P1_up, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(gpio_P1_down, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(gpio_P2_up, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(gpio_P2_down, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(gpio_Replay, gpio.IN, pull_up_down=gpio.PUD_UP)   

#
# Buttons check
#

def checkButton(keys_pressed,key,gpio_pin):
    if keys_pressed[key]:
        return True
    if GPIO_READY:
        return gpio_pin and gpio.input(gpio_pin)==False
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
        self.speed = 2
        self.walls = None
        self.controls = controls
        self.bounce_direction=1
        self.gpio_up=None
        self.gpio_down=None
        
    def update(self):
       
        direction = 0
        keys_pressed = pygame.key.get_pressed()

        if checkButton(keys_pressed,self.controls.up_key,self.gpio_up):
            direction -= 1

        if checkButton(keys_pressed,self.controls.down_key,self.gpio_down):
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
        self.speed = 2
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
        self.set_value_to(0)
        
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
        self._surface=None

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
        self._surface=surface

        if self.need_bg:
            self.need_bg=False
            self.bg.blit(self._top_wall.image,[self._top_wall.rect.x,self._top_wall.rect.y])
            self.bg.blit(self._bottom_wall.image,[self._bottom_wall.rect.x,self._bottom_wall.rect.y])
            surface.blit(self.bg,[0,0])
            pygame.display.update()
    
        State.on_render(self,surface)
    
    def on_cleanup(self):
        self._surface.blit(self.bg,[0,0])
        pygame.display.update()
        
    
#
# Title State
#
class TitleState(AbstractState):
    def __init__(self):
        AbstractState.__init__(self)
        title = title_font.render('GET READY',False,FOREGROUND)

        self.p1_title=pygame.transform.rotate(title,270)
        self.p2_title=pygame.transform.rotate(title,90)

    def on_loop(self):
        AbstractState.on_loop(self)
    
    def on_render(self,surface):
        self.need_bg=True
        AbstractState.on_render(self,surface)
        
        h_mid=.5*(SCREEN_H-self.p1_title.get_height());

        surface.blit(self.p1_title,[.25*SCREEN_W-.5*self.p1_title.get_width(),h_mid])
        surface.blit(self.p2_title,[.75*SCREEN_W-.5*self.p2_title.get_width(),h_mid])
        pygame.display.update()
        sleep(3)
        GAME_STATE.reset()
        StateManager.currentState=GAME_STATE

#
# Girls State
#
class GirlsState(State):
    def __init__(self):
        State.__init__(self)
        self.title = title_font.render('YOUR PONG IS SO LONG',False,FOREGROUND)
        self.girls=None
        
    def on_loop(self):
        State.on_loop(self)
    
    def on_render(self,surface):
        State.on_render(self,surface)

        surface.fill(BACKGROUND)

        if not self.girls:
            self.girls = pygame.transform.scale2x(girls_img)    
        
        surface.blit(self.girls,[SCREEN_W-self.girls.get_width(),SCREEN_H-self.girls.get_height()])

        surface.blit(self.title,[20,40])
        
        pygame.display.update()
        sleep(5)
        GAME_STATE.reset()
        StateManager.currentState=TITLE_STATE

            
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
        self._paddle_1.gpio_up = gpio_P1_up
        self._paddle_1.gpio_down = gpio_P1_down
        
        self._paddle_2 = Paddle(FOREGROUND,PADDLE_W,PADDLE_H,controls2)
        self._paddle_2.move(SCREEN_W - PADDLE_MARGIN_H - self._paddle_2.rect.w,self._paddle_1.rect.y)
        self._paddle_2.bounce_direction=-1
        self._paddle_2.gpio_up = gpio_P2_up
        self._paddle_2.gpio_down = gpio_P2_down

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
        
    def on_event(self,event):
        keys_pressed = pygame.key.get_pressed()

        if checkButton(keys_pressed,REPLAY_KEY,gpio_Replay):
            print gpio_Replay
            StateManager.currentState=TITLE_STATE
            
    def render_counter(self,count):
        return font.render(str(count),False,FOREGROUND)

    def reset(self):
        self._score1=0
        self._score2=0

        self._counter1.set_value_to(self._score1)
        self._counter1.rect.x = .5*SCREEN_W-40-self._counter1.rect.w
        self._counter1.rect.y = 16
        
        self._counter2.set_value_to(self._score2)
        self._counter2.rect.x = .5*SCREEN_W+50
        self._counter2.rect.y = 16

        self._ball.respawn()

        self._paddle_1.move(PADDLE_MARGIN_H,.5*(SCREEN_H- self._paddle_1.rect.h))
        self._paddle_2.move(SCREEN_W - PADDLE_MARGIN_H - self._paddle_2.rect.w,self._paddle_1.rect.y)
            
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
                sleep(1)
                StateManager.currentState=GIRLS_STATE
        
            self._counter2.set_value_to(self._score2)
            self._counter2.rect.x = .5*SCREEN_W+50
            self._counter2.rect.y = 16
            self._ball.respawn()
            
        if self._ball.rect.left>SCREEN_W:
            self._score1+=1;
            
            if self._score1>99:
                sleep(1)
                StateManager.currentState=GIRLS_STATE

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
        pygame.mouse.set_visible(False)
        
        self._running = True
        self._clock = pygame.time.Clock()

        try:
            global wall_sfx
            wall_sfx = pygame.mixer.Sound('assets/wall_blip.wav')  #load sound
            global paddle_sfx
            paddle_sfx = pygame.mixer.Sound('assets/paddle_blip.wav')  #load sound
        except:
            raise UserWarning, "could not load or play soundfiles in 'data' folder :-("

        global girls_img
        girls_img = pygame.image.load("assets/cga_girls4.gif").convert()

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
        
        if GPIO_READY:
            GPIO.cleanup()

if __name__ == "__main__":

    pygame.mixer.pre_init(44100, -16, 2, 2048)
    
    theApp = App(SCREEN_W,SCREEN_H)

    TITLE_STATE = TitleState()
    GAME_STATE = GameState()
    GIRLS_STATE = GirlsState()
    StateManager.currentState = GIRLS_STATE
    theApp.on_execute()
        
    

