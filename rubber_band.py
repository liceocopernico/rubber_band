import matplotlib
matplotlib.use("Agg")
import pylab
import configparser 
import os
import pygame
from physical_elements import rubber_band,moving_observer
from graphics import text_renderer
from event_manager import Notifier



config = configparser.ConfigParser()
current_path=os.path.dirname(os.path.realpath(__file__))
config.read(current_path+"/config.ini")




screen_x=int(config['screen']['screenx'])
screen_y=int(config['screen']['screeny'])


fig = pylab.figure(figsize=[int(screen_x/int(config['graphs']['resolution'])),int(config['graphs']['height'])],dpi=int(config['graphs']['resolution']))
graph_size=(screen_x,int(config['graphs']['height'])*int(config['graphs']['resolution']))

fps=int(config['rubber_band']['fps'])


pygame.init()

screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Rubber band simulation")
clock = pygame.time.Clock()



str_spring=rubber_band(float(config['rubber_band']['length']),
                       float(config['rubber_band']['mass']),
                       int(config['rubber_band']['beads_number']),
                       float(config['rubber_band']['cross_section']),
                       float(config['rubber_band']['y_mod']),
                       float(config['rubber_band']['max_disp']))


observer=moving_observer(pygame.Vector2(0,0),
                        float(config['rubber_band']['length']),
                        float(config['rubber_band']['max_disp']),
                        str_spring)

informations=text_renderer()


notifier=Notifier()

def quit_simulation():
    pygame.quit()
    quit()




notifier.subscribe(pygame.QUIT,quit_simulation)

notifier.subscribe(pygame.MOUSEBUTTONDOWN,observer)
notifier.subscribe(pygame.KEYUP,observer)
notifier.subscribe(pygame.MOUSEMOTION,observer)
notifier.subscribe(pygame.MOUSEWHEEL,observer)
notifier.subscribe(pygame.MOUSEBUTTONUP,str_spring)
notifier.subscribe(pygame.MOUSEMOTION,str_spring)
notifier.subscribe(pygame.MOUSEBUTTONDOWN,str_spring)
notifier.subscribe(pygame.KEYUP,str_spring)
notifier.subscribe(pygame.MOUSEWHEEL,str_spring)


informations.subscribe(str_spring)


while True:
    clock.tick(fps)
    
    
    notifier.dispatch(pygame.event.get(),screen)
    
    screen.fill("white")
        
    str_spring.compute_forces_accel()
    str_spring.compute_velocity()
    str_spring.compute_position()
    str_spring.draw_time_domain(screen,fig,graph_size, config['graphs']['rendering_mode'],screen_y)
    str_spring.draw_fft(screen,fig,graph_size, config['graphs']['rendering_mode'],screen_y)
    str_spring.draw_forces(screen)
    str_spring.draw_connected_beads(screen)
    
    observer.render_rubber_band(screen)
    
    
    observer.draw_observer(screen)
    observer.update_observer_position()
  
    informations.dispatch(screen)
  
    pygame.display.flip()

    
     
q