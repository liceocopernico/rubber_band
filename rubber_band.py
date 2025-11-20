import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import configparser 
import os
import pygame
import pygame.freetype 
from physical_elements import rubber_band


config = configparser.ConfigParser()
current_path=os.path.dirname(os.path.realpath(__file__))
config.read(current_path+"/config.ini")
fig = pylab.figure(figsize=[int(config['graphs']['width']),int(config['graphs']['height'])],dpi=int(config['graphs']['resolution']))
graph_size=(int(config['graphs']['width'])*int(config['graphs']['resolution']),int(config['graphs']['height'])*int(config['graphs']['resolution']))

screen_x=1280
screen_y=1200


pygame.init()
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Rubber band simulation")
clock = pygame.time.Clock()
running = True
dt = 0
pygame.font.init() 

sim_font = pygame.freetype.Font("Lato_Heavy.ttf", 18)


str_spring=rubber_band(0.5,0.6,int(config['rubber_band']['beads_number']),0.05,450.0)

anchor=None

evolution=False
forces=False
armonic=1
time=0
frames=0
raw_data=str_spring.draw_fft(fig,0.01,1.0)
if config['graphs']['beads_draw_mode']=="connected":
    draw_connected=True
else:
    draw_connected=False

    
surf = pygame.image.frombytes(raw_data,graph_size, config['graphs']['rendering_mode'])
show_spectrum=False
show_time_domain=False
max_freq=1.0

while running:
    frames+=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            anchor=None
            if event.button == 1:
                anchor=str_spring.get_bead_anchor(event.pos)
                print(f"Anchor aquired position ")
                
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                anchor=None
                print(f"Anchor released")
        if event.type == pygame.MOUSEMOTION:
          
            if anchor!=None:
                str_spring.move_bead(anchor,event.pos,screen)
            
        if event.type== pygame.KEYUP:
                print(event.key)
                match event.key:
                    case pygame.K_s:
                        evolution=not evolution
                    case pygame.K_f:
                        forces=not forces
                    case pygame.K_r:
                        evolution=False
                        str_spring.reset()
                    case pygame.K_a:
                        str_spring.set_n_armonic(1,0.25)
                    case pygame.K_b:
                        str_spring.set_impulse1()
                    case pygame.K_c:
                        str_spring.set_n_armonic(5,0.25)
                    case pygame.K_x:
                        armonic+=1
                        str_spring.set_n_armonic(armonic,0.25)
                    case pygame.K_l:
                        show_spectrum= not show_spectrum
                    case pygame.K_j:
                        max_freq+=0.1
                    case pygame.K_k:
                        max_freq-=0.1
                    case pygame.K_z:
                        armonic-=1
                        if armonic<1:
                            armonic=1
                        str_spring.set_n_armonic(armonic,0.25)
                    case pygame.K_o:
                        str_spring.set_n_m_armonic(3,7)
                    case pygame.K_t:
                        show_time_domain= not show_time_domain
                    case pygame.K_e:
                        draw_connected= not draw_connected
                
    screen.fill("white")
    
    dt = clock.tick(240)/200
    time+=dt
    
    sim_font.render_to(screen, (0, 0), f"dt {dt} time {round(time,4)} speed {round(str_spring.get_wave_speed(),4)}", (0, 0, 0))
    if evolution:
        
        str_spring.compute_forces_accel()
        str_spring.compute_velocity(dt)
        str_spring.compute_position(dt)
        if show_time_domain:
            if frames%100==0:
                fig.clear()
                raw_data=str_spring.draw_time_domain(fig,dt)
                
                surf = pygame.image.fromstring(raw_data, graph_size, config['graphs']['rendering_mode'])
                
            screen.blit(surf, (-0.9*int(config['graphs']['resolution']),screen_y-graph_size[1]))
        
        if show_spectrum:
            if frames%100==0:
                fig.clear()
                raw_data=str_spring.draw_fft(fig,dt,max_freq)
                
                surf = pygame.image.fromstring(raw_data, graph_size, config['graphs']['rendering_mode'])
                
            screen.blit(surf, (-int(config['graphs']['resolution']),screen_y-graph_size[1]))
 
    
    if forces and evolution:
        str_spring.draw_forces(screen)
    if draw_connected:
        str_spring.draw_connected_beads(screen)
    else:
        str_spring.draw_beads(screen)
    
    
    
    dt = clock.tick(240) 
    pygame.display.flip()

    
     
    
pygame.quit()