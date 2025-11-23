import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import configparser 
import os
import pygame
import pygame.freetype 
from physical_elements import rubber_band,movingObserver
import pygame_widgets
from pygame_widgets.button import Button

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

dt =1/float(config['rubber_band']['fps'])*float(config['rubber_band']['gamma'])

pygame.font.init() 


sim_font = pygame.freetype.Font("Lato_Heavy.ttf", 18)



str_spring=rubber_band(float(config['rubber_band']['length']),
                       float(config['rubber_band']['mass']),
                       int(config['rubber_band']['beads_number']),
                       float(config['rubber_band']['cross_section']),
                       float(config['rubber_band']['y_mod']),
                       float(config['rubber_band']['max_disp']))


observer=movingObserver(pygame.Vector2(0,0),
                        float(config['rubber_band']['length']),
                        float(config['rubber_band']['max_disp']),
                        str_spring)



def start_evolution():
    global evolution
    evolution=True
    button.setText("Stop")



button = Button(
    screen, 100, 100, 300, 150, text='Go',
    fontSize=50, margin=20,
    inactiveColour=(255, 0, 0),
    pressedColour=(0, 255, 0), radius=20,
    onClick=start_evolution
)
 
wave_speed=str_spring.get_wave_speed()
observer.speed=wave_speed

notifier=Notifier()

def quit_simulation():
    pygame.quit()
    quit()



notifier.subscribe(pygame.KEYUP,observer)
notifier.subscribe(pygame.QUIT,quit_simulation)
notifier.subscribe(pygame.MOUSEBUTTONDOWN,str_spring)
notifier.subscribe(pygame.MOUSEBUTTONDOWN,observer)
notifier.subscribe(pygame.MOUSEBUTTONUP,str_spring)
notifier.subscribe(pygame.MOUSEMOTION,str_spring)
notifier.subscribe(pygame.MOUSEMOTION,observer)
notifier.subscribe(pygame.KEYUP,str_spring)


while True:
    clock.tick(fps)
    
    
    
    notifier.dispatch(pygame.event.get(),screen)
    screen.fill("white")
    
    
    
   
    sim_font.render_to(screen, (10, 20), f"dt {dt}  time {round(str_spring.state['time'],4)}  speed {round(wave_speed,4)}   frames {str_spring.state['frames']}", (0, 0, 0))
    sim_font.render_to(screen, (10, 40), f"Kinetic Energy: {str_spring.T} potential energy {str_spring.U} total energy {str_spring.T+str_spring.U}" ,(240,120,100))
    
    str_spring.compute_forces_accel()
    str_spring.compute_velocity(dt)
    str_spring.compute_position(dt)
    str_spring.draw_forces(screen)
    str_spring.draw_connected_beads(screen)
    str_spring.draw_beads(screen)
    str_spring.draw_time_domain(screen,fig,dt,graph_size, config['graphs']['rendering_mode'],screen_y)
    str_spring.draw_fft(screen,fig,dt,graph_size, config['graphs']['rendering_mode'],screen_y)
    
    observer.draw_observer(screen)
    observer.update_observer_position(dt)
  
  
    pygame.display.flip()

    
     
    
pygame.quit()