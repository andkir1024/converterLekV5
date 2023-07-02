import math
import cv2
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry

from commonData import DirectionStatus, TypeСutout

class sequencer:
    def classifyPath(direction, approx, lineN):
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
            return TypeСutout.undifined, None
        if allSeq == 2:
            if seq[0][0]== DirectionStatus.dir90 and seq[1][0] == DirectionStatus.dir180:
                pp0, pp1, pp2= sequencer.calk3PointRect(approx, lineN)
                hasLines = sequencer.findParallelLines(approx)
                if hasLines == True:
                    return TypeСutout.UType1, (pp0, pp1, pp2)
                return TypeСutout.UType0, (pp0, pp1, pp2)
        if allSeq == 3:
            if seq[0][0]== DirectionStatus.dir180 and seq[1][0] == DirectionStatus.dir90 and seq[2][0] == DirectionStatus.dir180:
                pp0, pp1, pp2= sequencer.calk3PointRect(approx, lineN)
                return TypeСutout.UType1, (pp0, pp1, pp2)
            
        return TypeСutout.undifined, None

    def lenghtLine( pp0, pp1):
        lenLine = math.sqrt( ((pp0[0]-pp1[0])**2)+((pp0[1]-pp1[1])**2))
        return lenLine
    def lenghtContoureLine( contour):
        lines = []
        maxVal =0
        for index in range(len(contour)-1):
            pointS = contour[index]
            pointE = contour[index+1]
            lenLine = sequencer.lenghtLine( pointS[0], pointE[0])
            # if lenLine> maxVal:
                # maxVal = lenLine
            pp0 = Point(pointS[0][0],pointS[0][1])
            pp1 = Point(pointE[0][0],pointE[0][1])
            lines.append((lenLine, pp0, pp1))
        lines = sorted(lines, key=lambda x: x[0], reverse=True)
        return lines

    def findParallelLines(approx):
        peri = cv2.arcLength(approx,False)/10
        lines = sequencer.lenghtContoureLine(approx)
        if len(lines)>3:
            lineA = lines[0]
            lineB = lines[1]
            dxA = abs(lineA[1].x-lineA[2].x)
            dxB = abs(lineB[1].x-lineB[2].x)
            boreder = 10
            if dxA < boreder and dxB  < boreder and lineA[0]>peri and lineB[0]>peri:
                return True
        return False

    # крание и центральная нижняя точка
    def calk3PointRect(approx, lineN):
        # pp0 = Point(approx[0][0][0],approx[0][0][1])
        # pp2 = Point(lineN[0][0],lineN[0][1])
        # # pp2 = Point(approx[-1][0][0],approx[-1][0][1])
        # pp1 = approx[0]

        pp0 = Point(lineN[0][0],lineN[0][1])
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

