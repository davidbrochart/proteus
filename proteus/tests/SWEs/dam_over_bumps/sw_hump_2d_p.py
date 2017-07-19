from proteus import *
from proteus.default_p import *
from proteus.mprans import SW2D
from proteus.mprans import SW2DCV
from proteus.Domain import RectangularDomain
import numpy as np
import math

nd=2

T=10.0#2*math.pi/omega
nDTout=100

L=(75.0,30.0)
g = 9.81
# PARAMETERS #
mannings=0.02

domain = RectangularDomain(L=L)

#This is relevant just when use_second_order_NonFlatB_with_EV_stabilization=True
cE=1
LUMPED_MASS_MATRIX=0

bt = domain.boundaryTags
bt['front'] = bt['bottom']
bt['back'] = bt['top']
domain.writePoly("tank2d")

######################
##### BATHYMETRY #####
######################
def bathymetry_function(X):
    import numpy as np
    x = X[0]
    y = X[1] 
    bump1 = 1-1./8*np.sqrt((x-30)**2+(y-6)**2)
    bump2 = 1-1./8*np.sqrt((x-30)**2+(y-24)**2)
    bump3 = 3-3./10*np.sqrt((x-47.5)**2+(y-15)**2)
    
    return np.maximum(np.maximum(np.maximum(0.,bump1),bump2),bump3)

##############################
##### INITIAL CONDITIONS #####
##############################
class water_height_at_t0:
    def uOfXT(self,X,t):
        x = X[0]
        if (x <= 16):
            eta=1.875
        else:
            eta=0.

        z = bathymetry_function(X)
        return max(eta - z,0.)

class Zero:
    def uOfXT(self,x,t):
        return 0.0

initialConditions = {0:water_height_at_t0(),
                     1:Zero(),
                     2:Zero()}

###################################
##### FOR BOUNDARY CONDITIONS #####
###################################
def getDBC_h(x,flag):
    return None

#note, these are the same for hu and hv so we can cheat and use  this p-file for SW2DCV and SW2D
def getDBC_u(x,flag):
   if (x[0] in [0.0,L[0]]) or flag in [bt['left'],bt['right']]:
       return lambda x,t: 0.0
   else:
       return None

def getDBC_v(x,flag):
   if x[1] in [0.0,L[1]] or flag in [bt['front'],bt['back']]:
       return lambda x,t: 0.0
   else:
       return None

dirichletConditions = {0:getDBC_h,
                       1:getDBC_u,
                       2:getDBC_v}

fluxBoundaryConditions = {0:'outFlow',
                          1:'outFlow',
                          2:'outFlow'}

def getAFBC_h(x,flag):
    return lambda x,t: 0.0

def getAFBC_u(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None
def getAFBC_v(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

advectiveFluxBoundaryConditions =  {0:getAFBC_h,
                                    1:getAFBC_u,
                                    2:getAFBC_v}

def getDFBC_u(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

def getDFBC_v(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

diffusiveFluxBoundaryConditions = {0:{},
                                   1:{1:getDFBC_u},
                                   2:{2:getDFBC_v}}

#########################################
##### CREATE MODEL AND COEFFICIENTS #####
#########################################
bathymetry={0:bathymetry_function}
LevelModelType = SW2DCV.LevelModel
coefficients = SW2DCV.Coefficients(g=g,bathymetry=bathymetry,cE=cE,LUMPED_MASS_MATRIX=LUMPED_MASS_MATRIX,mannings=mannings)

