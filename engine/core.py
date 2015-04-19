import pygame,sys
from pygame.locals import *

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
# Main Apllication Class
#
class App:

    def __init__(self,width,height,fps):
        self._runnting = True
        self._display_surf = None
        self.size = width,height
        self.fps = fps
        self.caption="Title"
        self._curStateIndex=0

    def on_init(self):
        pygame.init()
        
        self._display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.caption)

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

            pygame.display.flip()
            self._clock.tick(self.fps)

        self.on_cleanup()
