import pygame
import pygame.freetype 
import math
from numpy.fft import fft
import numpy as np
from buffers import timeCirBuffer
import matplotlib
import matplotlib.backends.backend_agg as agg
import configparser 
import os

class spring:
    def __init__(self,rest_length,k,mi):
        self.rest_length = rest_length
        self.k = k
        self.mi=mi
        
   
class bead:
    def __init__(self, position, r,mass):
        self.position=position
        self.velocity=pygame.Vector2(0,0)
        self.r = r
        self.color = "blue"
        
        self.mass=mass
        
        self.rectangle=pygame.Rect(0,0,0,0)
        
    def draw(self,screen,screen_size,length,max_disp):        
        screen_position=(self.position.x/length*screen_size[0],screen_size[1]/2-self.position.y/max_disp*screen_size[1])
        self.rectangle=pygame.Rect(screen_position[0]-self.r,screen_position[1]-self.r,2*self.r,2*self.r)
        pygame.draw.circle(screen, self.color, screen_position, self.r,)
    
    def get_collision(self,pos):
        if self.rectangle.collidepoint(pos):
           return self
        return None

class rubber_band:
    def __init__(self,length,mass,N,cross_section,y_mod):
        
        self.config = configparser.ConfigParser()
        current_path=os.path.dirname(os.path.realpath(__file__))
        self.config.read(current_path+"/config.ini")
        self.length=length
        self.mass=mass
        self.N=N
        self.bead_mass=mass/N
        k_total=cross_section*y_mod/length
        self.k_spring=k_total/N
        self.beads=[]
        self.forces=[]
        self.mid_position=[]    
        self.w_size=int(self.config['fft']['window_size'])
        self.v_fraction=float(self.config['drawing']['vertical_fraction'])
        self.time_series=timeCirBuffer(np.arange(0,1,1/self.w_size),self.w_size)
        self.times=[]
        self.accelerations=[]
        self.springs=[]
        self.damping=float(self.config['rubber_band']['damping_factor'])
        self.max_disp=0.01 
        self.left=pygame.Vector2(0,0)
        self.right=pygame.Vector2(length,0)
        self.tension=0.5
        
        
        for i in range(N):
            self.springs.append(spring(self.tension*length/N,self.k_spring,self.damping))
        for i in range(N-1):
            pos=pygame.Vector2((i+1)*length/N,0)
            self.beads.append(bead(pos,3,self.bead_mass))
        for i in range(N-1):
            self.accelerations.append(pygame.Vector2(0,0))
            self.forces.append(pygame.Vector2(0,0))
    

    
    
    def _get_wave_fft(self,dt):
            
        sampling_rate=round(1/dt)
        np_amplitudes=self.time_series.to_array()
        f_domain=fft(np_amplitudes)
        N=len(f_domain)
        n = np.arange(N)
        T = N/sampling_rate
        freq = n/T      
        return (freq,np.abs(f_domain))
       
    def _get_simulation_size(self,screen):
        actual_size=pygame.display.get_window_size()
        screen_size=(actual_size[0],round(actual_size[1]*self.v_fraction))  
        return screen_size
    
    def draw_time_domain(self,screen):
       
        screen_size=self._get_simulation_size(screen)
                       
        N=2048
        
        for i in range(N):
            
            screen_position=((i+1)/N*screen_size[0],screen_size[1]/2-self.time_series.item_at(i)/self.max_disp*screen_size[1])
            
            pygame.draw.circle(screen, 'red', screen_position, 3)
    
    def draw_fft(self,figure,dt,max_freq):

        data=self._get_wave_fft(dt)
        axis=figure.gca()
        axis.plot(data[0],data[1])
        matplotlib.pyplot.xlim(0,max_freq)
        canvas = agg.FigureCanvasAgg(figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        print(canvas.get_width_height())
        return raw_data
                  
    def set_n_armonic(self,n,an):
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,an*self.max_disp*math.sin(n*math.pi/self.length*x_pos)    )


    def set_n_m_armonic(self,n,m):
        an=1.0/math.sqrt(2)*0.25
        
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,an*self.max_disp*math.sin(n*math.pi/self.length*x_pos)    )
            
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position.y+=2*an*self.max_disp*math.sin(m*math.pi/self.length*x_pos) 
        
    def set_impulse1(self):
        for i in range(int(self.N/10)):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,0.25*self.max_disp*math.sin(10*math.pi/self.length*x_pos)    )
       
    def reset(self):
        for i in range(self.N-1):
            self.forces[i]=pygame.Vector2(0,0)
            self.accelerations[i]=pygame.Vector2(0,0)
            self.beads[i].position=pygame.Vector2((i+1)*self.length/self.N,0)
            self.beads[i].velocity=pygame.Vector2(0,0)
            
    def get_support_tension(self):
        left_spring=self.left-self.beads[0].position
        left_force=self.springs[0].k*abs(left_spring.length()-self.springs[0].rest_length)
        right_spring=self.beads[self.N-2].position-self.right
        right_force=self.springs[self.N-1].k*abs(right_spring.length()-self.springs[self.N-1].rest_length)
        return (left_force,right_force)
    
    def get_wave_speed(self):
        s_tension=self.get_support_tension()
        speed=math.sqrt(self.length*s_tension[0]/self.mass) 
        return speed
    
    def compute_force(self,i):
        if i==0:
            preceding=self.left
        else:
            preceding=self.beads[i-1].position
        if i==self.N-2:
            following=self.right
        else:
            following=self.beads[i+1].position
         
        left_spring=self.beads[i].position-preceding
        left_length=left_spring.length()
        left_versor=left_spring/left_length
        right_spring=self.beads[i].position-following
        right_length=right_spring.length()
        right_versor=right_spring/right_length  
        left_force=-self.springs[i].k*abs(left_length-self.springs[i].rest_length)*left_versor
        right_force=-self.springs[i+1].k*abs(right_length-self.springs[i+1].rest_length)*right_versor
        
        total_force=left_force+right_force-self.damping*self.beads[i].velocity
        
        return [total_force,left_force,right_force]

    def compute_forces_accel(self):   
        for i in range(self.N-1):
               force=self.compute_force(i)
               accelleration=force[0]/self.beads[i].mass
               self.accelerations[i]=accelleration
               self.forces[i]=force

    def compute_velocity(self,dt):
        for i in range(self.N-1):
            self.beads[i].velocity+=self.accelerations[i]*dt
    
    def compute_position(self,dt):
        for i in range(self.N-1):
            self.beads[i].position+=self.beads[i].velocity*dt
        self.time_series.enqueue(self.beads[int(self.N/2)].position.y)
        #self.mid_position.append(self.beads[int(self.N/2)].position.y)
   
    def _translate_pixel(self,position,screen_size,length,max_disp):
        screen_position=(position.x/length*screen_size[0],screen_size[1]/2-position.y/max_disp*screen_size[1])
        return screen_position

    def move_bead(self,bead_index,mouse_pos,screen):
        
        screen_size=self._get_simulation_size(screen)
        new_y_pos=(screen_size[1]/2-mouse_pos[1])/screen_size[1]*self.max_disp
        print(new_y_pos)
        if abs(new_y_pos)>0.5*self.max_disp:
            new_y_pos=0.5*self.max_disp*np.sign(new_y_pos)
        
        system_position=pygame.Vector2(self.beads[bead_index].position.x,new_y_pos)
        self.beads[bead_index].position=system_position
        
    
    def draw_beads(self,screen):
        
        screen_size=self._get_simulation_size(screen)
        for bead in self.beads:
            bead.draw(screen,screen_size,self.length,self.max_disp)
    
    def get_bead_dynamics(self,i):
        return (self.beads[i].position,self.beads[i].velocity,self.accelerations[i])
    
    def draw_forces(self,screen):
       
        screen_size=self._get_simulation_size(screen)
        for i in range(self.N-1):
            start=self._translate_pixel(self.beads[i].position,screen_size,self.length,self.max_disp)
            
            end1=self._translate_pixel(self.beads[i].position+self.forces[i][1],screen_size,self.length,self.max_disp)
            end2=self._translate_pixel(self.beads[i].position+self.forces[i][2],screen_size,self.length,self.max_disp)
            #total=self._translate_pixel(self.beads[i].position+self.accelerations[i],screen_size,self.length,self.max_disp)
            pygame.draw.line(screen,'red',start,end1)
            pygame.draw.circle(screen, 'red', end1, 2,)
            pygame.draw.line(screen,'green',start,end2)
            pygame.draw.circle(screen, 'green', end2, 2,)
            #pygame.draw.line(screen,'black',start,total)
            #pygame.draw.circle(screen, 'black', total, 2,)
    
    def get_bead_anchor(self,mouse_pos):
        
        
        for i in range(self.N-1):
            if self.beads[i].get_collision(mouse_pos):
               return i
        return None

            
      

