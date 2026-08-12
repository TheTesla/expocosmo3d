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
    h = 150
    l_hld = 20 + 1
    w_hld = l_hld + 11 

    r_screws = 5.5/2
    z_screw = 30
    zd_screws = 40
    y_screws = -w_hld/2+l_hld/2

    outer = solid_model((x, y+t_wall, z, (rfase, rbottle+t_wall, h, w_hld, l_hld+2*t_wall, rfase)))
    inner = solid_model((x, y, z-t_wall, (rfase, rbottle, h+rfase+rcube, w_hld, l_hld, rcube)))
    hole_mid_profile = bd.fz_circle((x,y-y_screws), r_screws)
    holes_x = bd.fz_circle(((z-z_screw+zd_screws/2)%zd_screws-zd_screws/2,y-y_screws), r_screws)
    holes_y = cmb.fz_and_chamfer(rfase, bd.fz_circle(((z-z_screw+zd_screws/2)%zd_screws-zd_screws/2,x), r_screws), y-w_hld-t_wall)
    solid = cmb.fz_and_chamfer(rfase, outer, -inner, -hole_mid_profile, -holes_x, -holes_y, z-h+y*0.5)
    if solid > 0:
        return False

    return True


render.renderAndSave(model_function, "bottledock.stl", 0.5)

