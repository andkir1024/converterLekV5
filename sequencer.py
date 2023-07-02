import math
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry

from commonData import DirectionStatus, TypeСutout

class sequencer:
    def classifyPath(direction, approx):
        seq = []
        # выделение последовательностей
        prev = direction[0]
        param = (prev, 0)
        seq.append(param)
        all = len(direction)
        for index in range(1, len(direction)):
            dir = direction[index]
            if dir != prev:
                prev = dir
                param = (prev, index)
                seq.append(param)
            pass
        allSeq = len(seq)
        if allSeq <= 1:
            return TypeСutout.undifined
        if allSeq == 2:
            if seq[0][0]== DirectionStatus.dir90 and seq[1][0] == DirectionStatus.dir180:
                pp0, pp1, pp2= sequencer.calk3PointRect(approx)
                return TypeСutout.UType0, pp0, pp1, pp2
            
        return TypeСutout.undifined

    # крание и центральная нижняя точка
    def calk3PointRect(approx):
        pp0 = Point(approx[0][0][0],approx[0][0][1])
        pp2 = Point(approx[-1][0][0],approx[-1][0][1])
        pp1 = approx[0]
        x = pp0.x + ((pp2.x - pp0.x)/2)
        y = 0
        for pp in approx:
            y = max(y, pp[0][1])
            pass
        pp1 = Point(x,y)
        return pp0, pp1, pp2
    
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

