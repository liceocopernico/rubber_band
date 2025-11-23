# rubber_band
A very simple rubber band simulation without using PDE



# Installation

Install UV python virtual environment manager:

```

Debian and Ubuntu

apt install pipx

pipx install uv

```

clone repository into a directory of your choice, I chose ~/tmp/projects

```

cd ~/tmp/projects
git clone https://github.com/liceocopernico/rubber_band.git

```

now enter into project directory and sync python virtual environment

```

cd rubber_band
uv sync

```


You are now ready to test this simple simulation

```
uv run rubber_band.py

```


# Keyboard shortcuts


* __f__ toggle forces display
* __s__ toggle simulation evolution
* __r__ reset simulation
* __a__ preset rubber band first harmonic
* __b__ preset generic impulse
* __c__ preset fifth harmonic
* __x__ increment preset harmonic number
* __z__ decrement harmonic number
* __l__ toggle display of signal fft graph
* __t__ toggle display of time domain graph
* __j__ increment fft display frequency range
* __k__ decrement fft display frequency rage
* __o__ preset third and seventh harmonic
* __u__ toggle show beads
* __e__ toggle show springs
* __g__ increment force vector display scale
* __h__ decrement force vector display scale
* __left arrow__ move probe bead left
* __right arrow__ move probe bead right
* __w__ place moving observer


# Mouse interaction

* __beads__ You can grab rubber band simulation beads and drag them around with your mouse, this's a simple way to draw an arbitrary impulse and show its propagation.
* __observer__ You can move the wave observer around with your mouse



# Configuration file

All user configurable parameters are saved in config.ini.

```
[environment]
g=9.81

[fft]
window_size=32768

[rubber_band]
damping_factor=0.05
beads_number=150
rest_stretch=0.1
fps=250
gamma=0.0001
y_mod=11000000000
cross_section=0.0000032
length=0.5
mass=0.1
max_disp=0.01

[graphs]
resolution=100
height=5
rendering_mode=RGBX
beads_radius=6

[drawing]
vertical_fraction=0.75

[screen]
screenx=1500
screeny=1200

[fonts]
file=Lato_Heavy.ttf
size=15


```
* __g__ Local gravitational field magnitude
* __window_size__ Fft window size, the bigger the higher fft resolution you can get
* __damping_factor__ Viscous friction coefficient in kg/s
* __beads_number__ The number of beads in the rubbed band
* __rest_stretch__ The unstreched length of springs is ugual to unperturbed spring length multiplied by rest_stretch, this means that all springs are in a stretched state before impulse propagation
* __fps__ Simulation target frames per second
* __gamma__ Time dilation factor a value of 1 for gamma means 1 ms of simulation time is a 1ms of computer time
* __y_mod__ Young modulus of rubber band material
* __cross_section__ Rubber band cross cross_section
* __length__ Rubber band length
* __mass__ Rubber band mass
* __max_disp__ Max vertical displacement of beads
* __resolution__ Resolution, in dpi, of matplotlib graphs
* __height__ Height of matplotlib graphs
* __rendering_mode__ Use RGBX for maximum performance
* __beads_radius__ Beads circle plot beads_radius
* __screenx__ Simulation x size
* __screeny__ Simulation y size
* __vertical_fraction__ Space reserved for graphs
* __file__ Font file
* __size__ Font size