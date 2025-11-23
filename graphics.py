import pygame
import pygame.freetype 
import configparser 
import os

class text_renderer:
    def __init__(self):
        
        
        self.config = configparser.ConfigParser()
        current_path=os.path.dirname(os.path.realpath(__file__))
        self.config.read(current_path+"/config.ini")
        pygame.font.init()
        self.font = pygame.freetype.Font(self.config['fonts']['file'], float(self.config['fonts']['size']))
        self.font_size=float(self.config['fonts']['size'])
        self._subscribers=[]
        self._subscribers_data={}
                
    def subscribe(self,subscriber):
        if not subscriber in self._subscribers:
            self._subscribers.append(subscriber)
        else:
            print("Already registered")
    
    def unsubscribe(self,subscriber):
        
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)
        else:
            print("Not registered")
    
    def _format_data(self,data,screen):
        v_pos=0
        for key in data:
            v_pos+=self.font_size
            text=f"{data[key][0]}: {data[key][1]} {data[key][2]}"
            self.render(screen,(10,v_pos),text)
        
    def dispatch(self,screen):
        for subscriber in self._subscribers:
            if subscriber.state['frames']%100==0:
                self._subscribers_data[subscriber]=subscriber.get_physics_data()
                self._format_data(self._subscribers_data[subscriber],screen)
                     
            elif subscriber.state['frames']%100!=0 and subscriber in self._subscribers_data:
                self._format_data(self._subscribers_data[subscriber],screen)
            
    def render(self, screen, position, text):
        self.font.render_to(screen, position, text, (0,0,0))
