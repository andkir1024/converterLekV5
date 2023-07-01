import enum
import os
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from mathUtils import *

class directionStatus(enum.Enum):
    undefined = 3

    LR = 4
    # горизонтальную в вертикальная
    RD = 5
    RL = 6
    LD = 7
    # вертикальная в горизонтальную (вверх)
    DL = 8
    # вертикальная в вертикальную
    DD = 9
    
class directionCountoure:
    def calcDirection(lineA, lineB):
        # if lineA[1][0] >= 
        isAngleA= directionCountoure.isAngle(lineA, 0.9)
        isAngleB= directionCountoure.isAngle(lineB, 0.9)
        if isAngleA == 1 and isAngleB ==2:
            return directionStatus.RD
        if isAngleA == 2 and isAngleB ==2:
            return directionStatus.DD
        if isAngleA == 2 and isAngleB ==1:
            return directionStatus.DL
        
        angleA=  directionCountoure.get_angleP(lineA)
        angleB=  directionCountoure.get_angleP(lineB)
        angleAGrad = math.radians(angleA)
        angleBGrad = math.radians(angleB)
        return directionStatus.undefined

    # 2 vertical line
    # 1 horizontal line
    # 0 angle line
    def isAngle(line, border):
        dx = abs(line[1][0] - line[0][0])
        dy = abs(line[1][1] - line[0][1])
        len = math.sqrt(dx**2+dy**2)
        coffx = dx / len 
        coffy = dy / len 
        if coffx > border:
            return 1
        if coffy > border:
            return 2
        return 0
    def get_angleP(line) -> float:
        dx = line[1][0] - line[0][0]
        dy = line[1][1] - line[0][1]
        rads = math.atan2(-dy,dx)
        rads %= 2*math.pi
        return rads

        # start, end = Point(line[0][0],line[0][1]),Point(line[1][0],line[1][1])
        # if end.y - start.y == 0:  # Avoids dividing by zero.
        #     return math.acos(0)
        # return -math.atan((end.x - start.x) / (end.y - start.y))

    # def getParamVector(pointS, pointF):
    #     deltax = pointS[0] - pointF[0]
    #     deltay = pointS[1] - pointF[1]
    #     len = math.sqrt(deltax**2+deltay**2)
    #     rad = bezier.get_angleP(Point(pointS[0],pointS[1]),Point(pointF[0],pointF[1]))
    #     angle = math.degrees(rad)
    #     return  (int(len), int(angle))
