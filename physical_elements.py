import pygame
import math
from numpy.fft import fft
import numpy as np
from buffers import timeCirBuffer
import matplotlib
import matplotlib.backends.backend_agg as agg
import configparser 
import os




        


class spring:
    def __init__(self,unp_length,rest_strech,k,mi):
        self.unp_length = unp_length
        self.k = k
        self.rest_length=unp_length*rest_strech
        self.length=unp_length
        self.U=0.5*self.k*(self.unp_length-self.rest_length)**2
    
    def set_length(self,length):
         self.length=length
         self.U=0.5*self.k*(self.length-self.rest_length)**2
         return self.U   
   
class bead:
    def __init__(self, position, r,mass):
        self.position=position
        self.velocity=pygame.Vector2(0,0)
        self.r = r
        self._color = "blue"
        self.mass=mass
        self.rectangle=pygame.Rect(0,0,0,0)
        self.T=0.0
        self.U=0.0
        
    def draw(self,screen,screen_size,length,max_disp):        
        screen_position=(self.position.x/length*screen_size[0],screen_size[1]/2-self.position.y/max_disp*screen_size[1])
        self.rectangle=pygame.Rect(screen_position[0]-self.r,screen_position[1]-self.r,2*self.r,2*self.r)
        pygame.draw.circle(screen, self._color, screen_position, self.r,)
    
    def get_collision(self,pos):
        if self.rectangle.collidepoint(pos):
           return self
        return None
    def set_kinetic_energy(self):
        self.T=0.5*self.mass*self.velocity.magnitude_squared()
        
    def set_potential_energy(self,g):
        self.U=self.mass*g*self.position.y
      
    def set_bead_color(self,color):    
        self._color=color
        
class rubber_band:
    def __init__(self,length,mass,N,cross_section,y_mod,max_disp):
        
        self.config = configparser.ConfigParser()
        current_path=os.path.dirname(os.path.realpath(__file__))
        self.config.read(current_path+"/config.ini")
        self.length=length
        self.mass=mass
        self.N=N
        self.bead_mass=mass/N
        self.cross_section=cross_section
        k_total=cross_section*y_mod/length
        self.k_spring=N*k_total
        self.y_mod=y_mod
        self.beads=[]
        self.forces=[]
        self.probe_bead=int(self.N/2)
        self.g=float(self.config['environment']['g'])   
        self.w_size=int(self.config['fft']['window_size'])
        self.v_fraction=float(self.config['drawing']['vertical_fraction'])
        self.time_series=timeCirBuffer(np.arange(self.w_size)*0.0,self.w_size)
        self.times=[]
        self.accelerations=[]
        self.springs=[]
        self.damping=float(self.config['rubber_band']['damping_factor'])
        self.max_disp=max_disp
        self.left=pygame.Vector2(0,0)
        self.right=pygame.Vector2(length,0)
        self.rest_stretch=float(self.config['rubber_band']['rest_stretch'])
        self.anchor=None
        self.surf=None
        self.dt =1/float(self.config['rubber_band']['fps'])*float(self.config['rubber_band']['gamma'])
               
        
        for i in range(N):
            self.springs.append(spring(length/N,self.rest_stretch,self.k_spring,self.damping))
        for i in range(N-1):
            pos=pygame.Vector2((i+1)*length/N,0)
            self.beads.append(bead(pos,int(self.config['graphs']['beads_radius']),self.bead_mass))
        for i in range(N-1):
            self.accelerations.append(pygame.Vector2(0,0))
            self.forces.append(pygame.Vector2(0,0))
        
        self.state=self._set_init_state()
        self.T=0.0
        self.U=self.get_potential_energy()
        self.beads[self.probe_bead].set_bead_color('red')
        
        
    def get_physics_data(self):
        data={  'time':["Time",round(self.state['time'],8),"s"],
                'frames':["Frames",self.state['frames'],""],
                'kinetic_energy':["Kinetic energy",round(self.T,8),"J"],
                'potential_energy':["Potential energy",round(self.U,8),"J"],
                'total_energy':["Total energy",round(self.T+self.U,8),"J"],
                'wave_speed':["Wave speed",round(self.get_wave_speed(),8),"m/s"],
                'friction':["Viscous friction coefficient",self.damping,"kg/s"],
                'mass':["Mass",self.mass,"kg"],
                'cross_section':["Cross section",self.cross_section,"m^2"],
                'length':["Length",self.length,"m"],
                'young_modulus':["Young modulus",self.y_mod,"Pa"],
                'g_field':["Gravity field modulus",self.g,"m/s^2"],
                'max_disp':["Max vertical displacement",self.max_disp,"m"]
        }
        return data
        
   
    def handle_event(self,event,screen):
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    self.anchor=self.get_bead_anchor(event.pos)
                    if self.anchor:
                        print(f"Anchor aquired position ")
            case pygame.MOUSEMOTION:    
                if self.anchor:
                    self.move_bead(self.anchor,event.pos,screen)
            case pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.anchor:
                        print(f"Anchor released")
                    self.anchor=None
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_f:
                        self.state['forces']=not self.state['forces']
                    case pygame.K_s:
                        self.state['frames']=0
                        self.state['evolution']=not self.state['evolution']
                    case pygame.K_r:
                        self.reset()
                    case pygame.K_a:
                        self.set_n_harmonic(1,0.25)
                    case pygame.K_b:
                        self.set_impulse1()
                    case pygame.K_c:
                        self.set_n_harmonic(5,0.25)
                    case pygame.K_x:
                        self.state['harmonic']+=1
                        self.set_n_harmonic(self.state['harmonic'],0.25)
                    case pygame.K_z:
                        self.state['harmonic']-=1
                        if self.state['harmonic']<1:
                            self.state['harmonic']=1
                        self.set_n_harmonic(self.state['harmonic'],0.25)
                    case pygame.K_l:
                        self.state['freq_domain']= not self.state['freq_domain']
                        self.state['time_domain'] =False
                        self.surf=None
                    case pygame.K_t:
                        self.state['time_domain']= not self.state['time_domain']
                        self.state['freq_domain']=False
                        self.surf=None
                    case pygame.K_j:
                        self.state['max_freq']+=0.1*self.get_zeroth_freq()
                    case pygame.K_k:
                        self.state['max_freq']-=0.1*self.get_zeroth_freq()
                    
                    case pygame.K_o:
                        self.set_n_m_harmonic(3,7)
                    case pygame.K_e:
                        self.state['connected']= not self.state['connected']
                        
                    case pygame.K_u:
                        self.state['beads']= not self.state['beads'] 
                    case pygame.K_g:
                        self.state['force_scale']*=0.5
                        
                    case pygame.K_h:
                        self.state['force_scale']*=2                   
                        if self.state['force_scale']>2:
                            self.state['force_scale']=1 
                    case pygame.K_LEFT:
                        self.beads[self.probe_bead].set_bead_color('blue')
                        self.probe_bead-=1
                        if self.probe_bead<0:
                            self.probe_bead=0
                        self.beads[self.probe_bead].set_bead_color('red')
                    case pygame.K_RIGHT:
                        self.beads[self.probe_bead].set_bead_color('blue')
                        self.probe_bead+=1
                        self.probe_bead=self.probe_bead%(self.N-1)
                        self.beads[self.probe_bead].set_bead_color('red')
    
    def _set_init_state(self):
        state={'frames':0,
               'forces':False,
               'freq_domain':False,
               'time_domain':False,
               'time':0.0,
               'evolution':False,
               'harmonic':1,
               'connected':False,
               'beads':True,
               'force_scale':1.0,
               'max_freq':2*self.get_zeroth_freq(),
               
               }
        return state
    
    def _get_wave_fft(self):
            
        sampling_rate=round(1/self.dt)
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
 
    def get_zeroth_freq(self):
        base_freq=self.get_wave_speed()/(2*self.length)
        return base_freq

    def get_potential_energy(self):
        energy=0
        for spring in self.springs:
            energy+=spring.U
        for bead in self.beads:
            energy+=bead.U
        return energy
    
    def get_kinetic_energy(self):
        energy=0
        for bead in self.beads:
            energy+=bead.T
        return energy
    
    def draw_time_domain(self,screen,figure,graph_size,rendering_mode,screen_y):
        
        if not self.state['time_domain'] or not self.state['evolution']:
            return
        
        if self.state['frames']%100==0:
            figure.clear()
            np_amplitudes=self.time_series.to_array()
            N=len(np_amplitudes)
            n = np.arange(N)
            t=n*self.dt
            axis=figure.gca()
            axis.plot(t,np_amplitudes)
            matplotlib.pyplot.ylabel('Amplitude (m)')
            matplotlib.pyplot.xlabel('Time (s)')
            canvas = agg.FigureCanvasAgg(figure)
            canvas.draw()
            renderer = canvas.get_renderer()
            
            raw_data = renderer.buffer_rgba()
            self.surf = pygame.image.frombuffer(raw_data, graph_size, rendering_mode)
            screen.blit(self.surf, (-0.9*int(self.config['graphs']['resolution']),screen_y-graph_size[1]))
        
        if self.surf:
            screen.blit(self.surf, (-0.9*int(self.config['graphs']['resolution']),screen_y-graph_size[1]))
          
    def draw_fft(self,screen,figure,graph_size,rendering_mode,screen_y):
        if not self.state['freq_domain'] or not self.state['evolution']:
            return
        
        if self.state['frames']%100==0:
            
            figure.clear()
            data=self._get_wave_fft(self.dt)
            axis=figure.gca()
            axis.plot(data[0],data[1])
            matplotlib.pyplot.xlim(0,self.state['max_freq'])
            matplotlib.pyplot.ylabel('FFT Amplitude squared mod')
            matplotlib.pyplot.xlabel('Frequency (Hz)')
            canvas = agg.FigureCanvasAgg(figure)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.buffer_rgba()
            self.surf = pygame.image.frombuffer(raw_data, graph_size, rendering_mode)
            screen.blit(self.surf, (-0.9*int(self.config['graphs']['resolution']),screen_y-graph_size[1]))
        if self.surf:
            screen.blit(self.surf, (-0.9*int(self.config['graphs']['resolution']),screen_y-graph_size[1]))
                          
    def set_n_harmonic(self,n,an):
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,an*self.max_disp*math.sin(n*math.pi/self.length*x_pos)    )
        self.update_band_U()

    def set_n_m_harmonic(self,n,m):
        an=1.0/math.sqrt(2)*0.25
        
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,an*self.max_disp*math.sin(n*math.pi/self.length*x_pos)    )
            
        for i in range(self.N-1):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position.y+=2*an*self.max_disp*math.sin(m*math.pi/self.length*x_pos) 
        self.update_band_U()
        
    def set_impulse1(self):
        for i in range(int(self.N/10)):
            x_pos=(i+1)*self.length/self.N
            self.beads[i].position=pygame.Vector2(x_pos,0.25*self.max_disp*math.sin(10*math.pi/self.length*x_pos)    )
        self.update_band_U()
        
    def reset(self):
        self.time_series=timeCirBuffer(np.arange(self.w_size)*0.0,self.w_size)
        self.state=self._set_init_state()
        for i in range(self.N-1):
            
            self.forces[i]=pygame.Vector2(0,0)
            self.accelerations[i]=pygame.Vector2(0,0)
            self.beads[i].position=pygame.Vector2((i+1)*self.length/self.N,0)
            self.beads[i].velocity=pygame.Vector2(0,0)
        self.update_band_U()
        self.update_band_T()
            
    def get_support_tension(self):
        left_spring=self.left-self.beads[0].position
        left_spring_stretch=abs(left_spring.length()-self.springs[0].rest_length)
        left_force=self.springs[0].k*left_spring_stretch
        
        
        right_spring=self.beads[self.N-2].position-self.right
        right_spring_stretch=abs(right_spring.length()-self.springs[self.N-1].rest_length)
        right_force=self.springs[self.N-1].k*right_spring_stretch
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
        
        gravity_versor=pygame.Vector2(0,-1)
        
        left_spring=self.beads[i].position-preceding
        left_length=left_spring.length()
        
        left_versor=left_spring/left_length
        right_spring=self.beads[i].position-following
        right_length=right_spring.length()
        right_versor=right_spring/right_length  
        
        
        left_spring_stretch=abs(left_length-self.springs[i].rest_length)
        left_force=-self.springs[i].k*left_spring_stretch*left_versor
        self.springs[i].set_length(left_length)
        
        
        right_spring_stretch=abs(right_length-self.springs[i+1].rest_length)    
        right_force=-self.springs[i+1].k*right_spring_stretch*right_versor
        self.springs[i+1].set_length(right_length)
        
        self.beads[i].set_kinetic_energy()
        self.beads[i].set_potential_energy(self.g)
        
        total_force=left_force+right_force-self.damping*self.beads[i].velocity+self.g*gravity_versor*self.beads[i].mass
        
        
        return [total_force,left_force,right_force]

    def compute_forces_accel(self):
        if not self.state['evolution']:
            return
       
        for i in range(self.N-1):
               force=self.compute_force(i)
               accelleration=force[0]/self.beads[i].mass
               self.accelerations[i]=accelleration
               self.forces[i]=force

    def compute_velocity(self):
        if not self.state['evolution']:
            return
        for i in range(self.N-1):
            self.beads[i].velocity+=self.accelerations[i]*self.dt
    
    def compute_position(self):
        if not self.state['evolution']:
            return
        for i in range(self.N-1):
            self.beads[i].position+=self.beads[i].velocity*self.dt
        self.time_series.enqueue(self.beads[self.probe_bead].position.y)
        self.state['time']+=self.dt
        self.state['frames']+=1
        if self.state['frames']%100==0:
            self.U=self.get_potential_energy()
            self.T=self.get_kinetic_energy()
            
    def update_band_U(self):
        for i in range(len(self.beads)):
            self.beads[i].set_potential_energy(self.g)
            if i==0:
                left_bead=self.left
            else:
                left_bead=self.beads[i-1].position
            spring_vector=self.beads[i].position-left_bead
            spring_length=spring_vector.length()
            self.springs[i].set_length(spring_length)
            
                
        last_spring=self.right-self.beads[len(self.beads)-1].position
        self.springs[len(self.beads)].set_length(last_spring.length())
        
        self.U=self.get_potential_energy()
    
    def update_band_T(self):
        for i in range(len(self.beads)):
            self.beads[i].set_kinetic_energy()
        self.T=self.get_kinetic_energy()
           
    def _translate_pixel(self,position,screen_size,length,max_disp):
        screen_position=(position.x/length*screen_size[0],screen_size[1]/2-position.y/max_disp*screen_size[1])
        return screen_position

    def move_bead(self,bead_index,mouse_pos,screen):
        
        screen_size=self._get_simulation_size(screen)
        new_y_pos=(screen_size[1]/2-mouse_pos[1])/screen_size[1]*self.max_disp
        
        if abs(new_y_pos)>0.5*self.max_disp:
            new_y_pos=0.5*self.max_disp*np.sign(new_y_pos)
        
        system_position=pygame.Vector2(self.beads[bead_index].position.x,new_y_pos)
        self.beads[bead_index].position=system_position
           
    def draw_connected_beads(self,screen):
        if not self.state['connected']:
            return
        screen_size=self._get_simulation_size(screen)        
        for i in range(self.N):
            if i==0:
                pass
                start=self._translate_pixel(self.left,screen_size,self.length,self.max_disp) 
                end=self._translate_pixel(self.beads[0].position,screen_size,self.length,self.max_disp) 
            elif i==self.N-1:
                start=self._translate_pixel(self.beads[i-1].position,screen_size,self.length,self.max_disp)
                end=self._translate_pixel(self.right,screen_size,self.length,self.max_disp)
            else:
               start=self._translate_pixel(self.beads[i-1].position,screen_size,self.length,self.max_disp)
               end=self._translate_pixel(self.beads[i].position,screen_size,self.length,self.max_disp) 
               
            pygame.draw.line(screen,'black',start,end,3)
    
    def draw_beads(self,screen):
        if not self.state['beads']:
            return
        screen_size=self._get_simulation_size(screen)
        for bead in self.beads:
            bead.draw(screen,screen_size,self.length,self.max_disp)
    
    def get_bead_dynamics(self,i):
        return (self.beads[i].position,self.beads[i].velocity,self.accelerations[i])
    
    def draw_forces(self,screen):
        if not self.state['forces'] or not self.state['evolution']:
            return
        
        scale=self.state['force_scale']
        screen_size=self._get_simulation_size(screen)
        for i in range(self.N-1):
            start=self._translate_pixel(self.beads[i].position,screen_size,self.length,self.max_disp)
            
            end1=self._translate_pixel(self.beads[i].position+scale*self.forces[i][1],screen_size,self.length,self.max_disp)
            end2=self._translate_pixel(self.beads[i].position+scale*self.forces[i][2],screen_size,self.length,self.max_disp)
            
            pygame.draw.line(screen,'red',start,end1)
            pygame.draw.circle(screen, 'red', end1, 2,)
            pygame.draw.line(screen,'green',start,end2)
            pygame.draw.circle(screen, 'green', end2, 2,)
          
    def get_bead_anchor(self,mouse_pos):
        
        
        for i in range(self.N-1):
            if self.beads[i].get_collision(mouse_pos):
               return i
        return None

class moving_observer:
    def __init__(self,position: pygame.Vector2,path_length,max_disp,rubber_band: rubber_band):
        self.position=position
        self.speed=rubber_band.get_wave_speed()
        self.observer = pygame.image.load('images/green_medium.png')
        self.observer_size=self.observer.get_size()
        self.path_length=path_length
        self.max_disp=max_disp
        self.place_observer=False
        self.observer_placed=False
        self.rubber_band=rubber_band
        self.dt=rubber_band.dt
        
    def _translate_pixel(self,position,screen_size,length,max_disp):
        screen_position=(position.x/length*screen_size[0],screen_size[1]/2-position.y/max_disp*screen_size[1])
        return screen_position
    
    def _get_simulation_size(self,screen):
        actual_size=pygame.display.get_window_size()
        screen_size=(actual_size[0],round(actual_size[1]))  
        return screen_size
    
    def handle_event(self,event,screen):
        match event.type:
            case pygame.KEYUP:
                if event.key==pygame.K_w:
                    self.place_observer=True
                    self.observer_placed=False
                    print("Place observer")
            case pygame.MOUSEMOTION:
                if self.place_observer:
                    self.set_observer_position_from_pixel(screen,event.pos)
            case pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    self.place_observer=False
                    self.observer_placed=True
            
    def set_observer_position_from_pixel(self,screen,mouse_pos):
        
        screen_size=self._get_simulation_size(screen)
        new_y_pos=(screen_size[1]/2-mouse_pos[1]+self.observer_size[1]*0.5)/screen_size[1]*self.max_disp
        new_x_pos=( mouse_pos[0]-self.observer_size[0]*0.5)/screen_size[0]*self.path_length
        observer_position=pygame.Vector2(new_x_pos,new_y_pos)
        self.position=observer_position
        
        
    def update_observer_position(self):
        if not self.rubber_band.state['evolution']:
            return
        
        self.position.x+=self.speed*self.dt
        if self.position.x>self.path_length:
            self.speed=-self.speed
            self.position.x=self.path_length
        elif self.position.x<0:
            self.speed=-self.speed
            self.position.x=0
    
    def draw_observer(self,screen):
        if self.place_observer or self.observer_placed:
            screen_size=self._get_simulation_size(screen) 
            screen_position=self._translate_pixel(self.position,screen_size,self.path_length,self.max_disp)
            screen.blit(self.observer,screen_position)