#!/usr/bin/env python3

from numba import njit
import numpy as np
from xyzcad import render
from fuzzyometry import bodies as bd
from fuzzyometry import combinations as cmb



@njit
def solid_model(p):
    x, y, z, param = p[:4]

    rfase, rbottle, h, w_hld, l_hld, rcube = param[:6]
    a = bd.fz_cuboid((x,y,z-h), (l_hld,w_hld,3*h), rcube)
    b = bd.fz_circle((x, y-rbottle), rbottle)
    return cmb.fz_and_chamfer(rfase, cmb.fz_or_chamfer(rfase, a, b), z-h, -z)


@njit
def model_function(p):
    x, y, z = p[:3]

    rfase = 3
    rcube = 1
    t_wall = 6
    rbottle = 50 +3
    h = 200
    l_hld = 20 + 1
    w_hld = l_hld + 11 

    r_screws = 5.5/2
    z_screw = 25
    zd_screws = 40
    y_screws = -w_hld/2+l_hld/2
    z_slot = 25
    h_slot = 20
    zd_slot = 40
    w_slot = 5
    ad_slot = 25

    rslts = (x**2 + (y-rbottle)**2)**0.5
    angslts = np.arctan2(x, y-rbottle)

    outer = solid_model((x, y+t_wall, z, (rfase, rbottle+t_wall, h, w_hld, l_hld+2*t_wall, rfase)))
    inner = solid_model((x, y, z-t_wall, (rfase, rbottle, h+rfase+rcube, w_hld, l_hld, rcube)))
    hole_mid_profile = bd.fz_circle((x,y-y_screws), r_screws)
    holes_x = bd.fz_circle(((z-z_screw+zd_screws/2)%zd_screws-zd_screws/2,y-y_screws), r_screws)
    holes_y = cmb.fz_and_chamfer(rfase, bd.fz_circle(((z-z_screw+zd_screws/2)%zd_screws-zd_screws/2,x), r_screws), y-w_hld-t_wall)
    #slots = bd.fz_cuboid((x,y-rbottle,(z-z_slot+zd_slot/2)%zd_slot-zd_slot/2),(2*(rbottle+t_wall+rfase), w_slot, h_slot), rfase)
    slots = bd.fz_cuboid((rslts, (angslts*rbottle+ad_slot/2)%ad_slot-ad_slot/2,(z-z_slot+zd_slot/2)%zd_slot-zd_slot/2),(2*(rbottle+t_wall+rfase), w_slot, h_slot), rfase)
    solid = cmb.fz_and_chamfer(rfase, outer, -inner, -hole_mid_profile, -holes_x, -holes_y, -slots, z-h+y*0.5)
    if solid > 0:
        return False

    return True


render.renderAndSave(model_function, "bottledock.stl", 0.5)

