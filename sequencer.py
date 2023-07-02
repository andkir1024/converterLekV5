import math
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry

from commonData import DirectionStatus

class sequencer:
    def checkPath(approx):
        directions = []
        for index in range(len(approx)-1):
            point = Point(approx[index][0][0],approx[index][0][1])
            pointN = Point(approx[index+1][0][0],approx[index+1][0][1])
            dir = sequencer.calkDir(point, pointN)
            directions.append(dir)
        return directions
    
    def calkDir(point, pointN):
        dx = point.x-pointN.x
        dy = -(point.y-pointN.y)

        if dx >= 0 and dy >= 0:
            return DirectionStatus.dir90
        if dx >= 0 and dy < 0:
            return DirectionStatus.dir180
        if dx < 0 and dy < 0:
            return DirectionStatus.dir270
        if dx < 0 and dy >= 0:
            return DirectionStatus.dir360


        # if dx == 0 and dy > 0:
        #     return DirectionStatus.dir0
        # if dx == 0 and dy < 0:
        #     return DirectionStatus.dir180
        # if dx > 0 and dy == 0:
        #     return DirectionStatus.dir90
        # if dx < 0 and dy == 0:
        #     return DirectionStatus.dir270
       
        # if dx >= 0 and dy >= 0:
        #     return DirectionStatus.dir0_90
        # if dx >= 0 and dy < 0:
        #     return DirectionStatus.dir90_180
        # if dx < 0 and dy < 0:
        #     return DirectionStatus.dir180_270
        # if dx < 0 and dy >= 0:
        #     return DirectionStatus.dir270_360
        
        # angle0 = geometryUtils.get_angle(0,0)
        # angle1 = geometryUtils.get_angle(1,0)
        # angle2 = geometryUtils.get_angle(1,-1)
        # angle4 = geometryUtils.get_angle(0,-1)
        # angle5 = geometryUtils.get_angle(-1,-1)
        # angle6 = geometryUtils.get_angle(-1,0)
        # angle7 = geometryUtils.get_angle(-1,1)
        return DirectionStatus.undifined
    
    def get_angle(dx, dy):
        if dy == 0:
            return math.degrees(math.acos(0))
        return math.degrees(-math.atan((dx) / (dy)))

