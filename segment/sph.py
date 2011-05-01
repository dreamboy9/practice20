import pygame
from pygame.locals import *
import numpy as np

from vector import Vec
from hash import Domain
from kernels import Kernel

#screen_scale = 160

class SPH:
    def __init__(self, max_num, domain, ghost_factor=1.):
        self.max_num = max_num

        rho0 = 1000.                #rest density [ kg/m^3 ]
        VF = .0262144               #simulation volume [ m^3 ]
        VP = ghost_factor * VF / max_num           #particle volume [ m^3 ]
        m = rho0 * VP               #particle mass [ kg ]
        re = (VP)**(1/3.)           #particle radius [ m ]
        #re = (VP)**(1/2.)           #particle radius [ m ]
        print "re, m, VP", re, m, VP
        rest_distance = .87 * re    #rest distance between particles [ m ]

        smoothing_radius = 2.0 * rest_distance      #smoothing radius for SPH Kernels
        boundary_distance = .5 * rest_distance      #for calculating collision with boundary
        
        #the ratio between the particle radius in simulation space and world space
        print "VF", VF
        print "domain.V: ", domain.V
        print "VF/domain.V", VF/domain.V
        print "scale calc", (VF/domain.V)**(1/3.)
        #print "scale calc", (VF/domain.V)**(1/2.)
        sim_scale = (VF / domain.V)**(1/3.)     #[m^3 / world m^3 ]
        #sim_scale = (VF / domain.V)**(1/2.)     #[m^2 / world m^2 ]

        self.rho0 = rho0
        self.VF = VF
        self.mass = m
        self.VP = VP
        self.re = re
        self.rest_distance = rest_distance
        self.smoothing_radius = smoothing_radius
        self.boundary_distance = boundary_distance
        self.sim_scale = sim_scale

        print "=====================================================" 
        print "particle mass:", self.mass
        print "Fluid Volume VF:", self.VF
        print "simulation scale:", self.sim_scale
        print "smoothing radius:", self.smoothing_radius
        print "rest distance:", self.rest_distance
        print "=====================================================" 

        #Other parameters
        self.K = 20.    #Gas constant
        self.boundary_stiffness = 100000.
        self.boundary_dampening = 512.
        #friction
        self.friction_coef = 0.
        self.restitution_coef = 0.
        #not used yet
        self.shear = 0.
        self.attraction = 0.
        self.spring = 0.

        self.velocity_limit = 600.
        self.xsph_factor = .5

        self.viscosity = .1
        self.gravity = -9.8
        #self.gravity = 0.

        self.EPSILON = 10E-6

        #Domain
        self.domain = domain
        self.domain.setup(self.smoothing_radius / self.sim_scale)
        print domain

        #Kernels
        self.kernels = Kernel(self.smoothing_radius)

    def make_struct(self, num):
        import struct
        print "make sph struct", num, self.max_num
        sphstruct = struct.pack('ffff'+
                    'ffff'+
                    'ffff'+
                    'ffff'+
                    'ffff'+
                    'ffff'+
                    'ffff'+
                    'iiii',
                    self.mass, self.rest_distance, self.smoothing_radius, self.sim_scale,
                    self.boundary_stiffness, self.boundary_dampening, self.boundary_distance, self.K,
                    self.viscosity, self.velocity_limit, self.xsph_factor, self.gravity,
                    self.friction_coef, self.restitution_coef, self.shear, self.attraction,
                    self.spring, self.EPSILON, np.pi, self.kernels.coeffs["poly6"],
                    0., 0., 0., self.kernels.coeffs["dspiky"],  #some kernels not used so coeffs
                    0., 0., 0., self.kernels.coeffs["ddvisc"],  #not calculated right now
                    num, 0, 0, self.max_num                         #nb_vars and coice not used
                    )
        return sphstruct


def toscreen(p, surface, screen_scale):
    translate = Vec([0,0])
    p.x = translate.x + p.x*screen_scale
    p.y = surface.get_height() - (translate.y + p.y*screen_scale)
    return p

class Particle:
    def __init__(self, pos, sphp, color, surface):
        #physics stuff
        self.pos = pos
        self.h = sphp.smoothing_radius
        self.scale = sphp.sim_scale
        self.mass = sphp.m

        self.vel = Vec([0.,0.])
        self.veleval = Vec([0.,0.])

        #pygame stuff
        self.col = color
        self.surface = surface
        self.screen_scale = self.surface.get_width() / sphp.domain.width

    def move(self, pos):
        self.pos = pos * self.scale

        #print "dens", self.dens

    def draw(self):
        #draw circle representing particle smoothing radius

        dp = toscreen(self.pos / self.scale, self.surface, self.screen_scale)
        pygame.draw.circle(self.surface, self.col, dp, self.screen_scale * self.h / self.scale, 1)
        #draw filled circle representing density
        pygame.draw.circle(self.surface, self.col, dp, self.dens / 40., 0)

        #TODO draw force vector (make optional)
        #vec = [self.x - f[0]*fdraw/fscale, self.y - f[1]*fdraw/fscale]
        #pygame.draw.line(self.surface, pj.col, self.pos, vec)

#std::vector<float4> addRect(int num, float4 min, float4 max, float spacing, float scale)
def addRect(num, pmin, pmax, sphp, global_color):
    #Create a rectangle with at most num particles in it.  The size of the return
    #vector will be the actual number of particles used to fill the rectangle
    print "**** addRect ****"
    print "rest dist:", sphp.rest_distance
    print "sim_scale:", sphp.sim_scale
    spacing = .99 * sphp.rest_distance / sphp.sim_scale;
    print "spacing", spacing

    xmin = pmin.x# * scale
    xmax = pmax.x# * scale
    ymin = pmin.y# * scale
    ymax = pmax.y# * scale

    print "min, max", xmin, xmax, ymin, ymax
    rvec = []
    color = []
    i=0
    import copy
    for y in np.arange(ymin, ymax, spacing):
        gcolor = copy.copy(global_color)
        for x in np.arange(xmin, xmax, spacing):
            if i >= num: break
            #print "x, y", x, y
            #rvec += [ Vec([x,y]) * sphp.sim_scale];
            rvec += [[x, y, 0., 1.]]
            #gcolor[3] += x / (xmax - xmin) *.0001
            #gcolor[0] = gcolor[3]
            color += [gcolor]
            

            i+=1;
    print "%d particles added" % i
    rvecnp = np.array(rvec, dtype=np.float32)
    colornp = np.array(color, dtype=np.float32)
    return rvecnp, colornp

def addPic(image, num, pmin, pmax, sphp):
    #Create a rectangle with at most num particles in it.  The size of the return
    #vector will be the actual number of particles used to fill the rectangle
    print "**** addPic ****"
    print "rest dist:", sphp.rest_distance
    print "sim_scale:", sphp.sim_scale
    #spacing = .99 * sphp.rest_distance / sphp.sim_scale;
    spacing = .70 * sphp.rest_distance / sphp.sim_scale;
    print "spacing", spacing

    xmin = pmin.x# * scale
    xmax = pmax.x# * scale
    ymin = pmin.y# * scale
    ymax = pmax.y# * scale

    print "min, max", xmin, xmax, ymin, ymax
    rvec = []
    color = []
    i=0

    ima = np.array(image)
    #ima.shape = (ima.shape[0] * ima.shape[1], )
    print ima.size
    print dir(image)
    print "COLORNP"
    yi = 0
    print image.size
    if len(image.size) == 2:
        ima = ima.T
    print image.size[0], image.size[1]

    for y in np.arange(ymax, ymin, -spacing):
        xi = 0
        if yi >= image.size[1]:
            break
        for x in np.arange(xmin, xmax, spacing):
            if i >= num: break
            xi += 1
            if xi >= image.size[0]:
                break

            #print "x, y", x, y
            #rvec += [ Vec([x,y]) * sphp.sim_scale];
            rvec += [[x, y, 0., 1.]]
            #print len(image.getpixel((xi,yi)))
            if len(image.size) == 2:
                #intensity = image.getpixel((xi, yi))/255.
                #g = ima.getpixl(xi, yi)/255.
                #b = ima[i*3+2]/255.
                intensity = ima[xi, yi] / 255. * .1
                r = intensity
                g = intensity
                b = intensity
                a = intensity / .1
                #print ima[xi]
                #print xi, yi
                color += [[r, g, b, a]]
            else:
                color += [ ima[yi, xi] /255. * .4 ]
            """
            r = ima[x,y,0]/255. * .1
            g = ima[x,y,1]/255. * .1
            b = ima[x,y,2]/255. * .1
            a = ima[x,y,3]/255. * .1
            color += [[r, g, b, a]]
            """
            i+=1;
        yi += 1
    print "%d particles added" % i
    rvecnp = np.array(rvec, dtype=np.float32)
    #print color
    colornp = np.array(color, dtype=np.float32)

    return rvecnp, colornp;



def addRect3D(num, pmin, pmax, sphp):
    #Create a rectangle with at most num particles in it.  The size of the return
    #vector will be the actual number of particles used to fill the rectangle
    print "**** addRect ****"
    print "rest dist:", sphp.rest_distance
    print "sim_scale:", sphp.sim_scale
    spacing = 1.1 * sphp.rest_distance / sphp.sim_scale;
    print "spacing", spacing

    xmin = pmin.x# * scale
    xmax = pmax.x# * scale
    ymin = pmin.y# * scale
    ymax = pmax.y# * scale
    zmin = pmin.z
    zmax = pmax.z

    print "min, max", xmin, xmax, ymin, ymax, zmin, zmax
    rvec = [];
    i=0;
    for z in np.arange(zmin, zmax, spacing):
        for y in np.arange(ymin, ymax, spacing):
            for x in np.arange(xmin, xmax, spacing):
                if i >= num: break
                print "x, y", x, y, z
                #rvec += [ Vec([x,y]) * sphp.sim_scale];
                rvec += [[x, y, z, 1.]]
                i+=1;
    print "%d particles added" % i
    rvecnp = np.array(rvec, dtype=np.float32)
    return rvecnp;




def init_particles(num, sphp, domain, surface):
    particles = []
    p1 = Vec([.5, 2.]) * sphp.sim_scale
    particles += [ Particle(p1, sphp, [255,0,0], surface) ] 

    pmin = Vec([.5, .5])
    pmax = Vec([2., 3.])
    ps = addRect(num, pmin, pmax, sphp)
    for p in ps:
        particles += [ Particle(p, sphp, [0,0,255], surface) ] 

    """
    p2 = Vec([400., 400.]) * sphp.sim_scale
    p3 = Vec([415., 400.]) * sphp.sim_scale
    p4 = Vec([400., 415.]) * sphp.sim_scale
    p5 = Vec([415., 415.]) * sphp.sim_scale
    p6 = Vec([430., 430.]) * sphp.sim_scale
    particles += [ Particle(p1, sphp, [255,0,0], surface) ] 
    particles += [ Particle(p2, sphp, [0,0,255], surface) ] 
    particles += [ Particle(p3, sphp, [0,205,0], surface) ] 
    particles += [ Particle(p4, sphp, [0,205,205], surface) ] 
    particles += [ Particle(p5, sphp, [0,205,205], surface) ] 
    particles += [ Particle(p6, sphp, [0,205,205], surface) ] 
    """
    return particles



if __name__ == "__main__":
    dmin = Vec([0.,0.,0.])
    dmax = Vec([500.,500.,1.])
    domain = Domain(dmin, dmax)
    system = SPH(2**14, domain)     #16384
    #system = SPH(2**12, domain)     #4096
