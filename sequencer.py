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
                hasLines, ppX0, ppX1, ppX2 = sequencer.findParallelLines(approx)
                if hasLines == True:
                    return TypeСutout.UType1, (pp0, pp1, pp2, ppX0, ppX1,ppX2)
                return TypeСutout.UType0, (pp0, pp1, pp2)
        if allSeq == 3:
            if seq[0][0]== DirectionStatus.dir180 and seq[1][0] == DirectionStatus.dir90 and seq[2][0] == DirectionStatus.dir180:
                pp0, pp1, pp2= sequencer.calk3PointRect(approx, lineN)
                hasLines, ppX0, ppX1,ppX2 = sequencer.findParallelLines(approx)
                sequencer.findParam4Lines(approx)
                return TypeСutout.UType2, (pp0, pp1, pp2, ppX0, ppX1, ppX2)
        if allSeq == 4:
            # hasLines, ppX0, ppX1,ppX2 = sequencer.findParallelLines(approx)
            param = sequencer.findParam4Lines(approx)
            ppS = sequencer.convertCoutoreToPoint(approx[0])
            ppE = sequencer.convertCoutoreToPoint(approx[-1])
            return TypeСutout.UType3, (param, ppS, ppE)
            
        return TypeСutout.undifined, None
    def convertCoutoreToPoint( countorePoint):
        point = Point(countorePoint[0][0],countorePoint[0][1])
        return point

    def findParam3Lines(approx):
        hasLines, ppX0, ppX1,ppX2 = sequencer.findParallelLines(approx)
    def findParam4Lines(approx):
        # peri = cv2.arcLength(approx,False)/25
        peri = cv2.arcLength(approx,False)/len(approx)
        lines = sequencer.lenghtContoureLine(approx, False)
        # выделение нормальных линия
        linesNew = []
        for line in lines:
            if line[0]> peri:
                linesNew.append(line)
        linesNew = list(reversed(linesNew))
        # выделение вертикальных линия
        border = 10
        start = False
        linesOut = []
        iS = -1
        canAddHorizont = False
        for line in linesNew:
            dx = abs(line[1].x-line[2].x)
            dy = abs(line[1].y-line[2].y)
            if dx < border:
                if start == False:
                    start = True
                    iE = line[5]
                    linesOut.append((line, 0))
                    canAddHorizont = False
                else:
                    start = False
                    iS = line[5]
                    point = sequencer.findMaxY(approx, iS, iE)
                    linesOut.append((line, 1, point))
                    canAddHorizont = True
            if dy < border and canAddHorizont:
                linesOut.append((line, -1, None))
        return linesOut
    
    def findMaxY( approx, iS, iE):
        y = 0
        point = Point(0,0)
        for index in range(iS, iE):
            pointY = approx[index][0][1]
            if pointY > y:
                y = pointY
                point = Point(approx[index][0][0],approx[index][0][1])
        return point
    
    def lenghtLine( pp0, pp1):
        lenLine = math.sqrt( ((pp0[0]-pp1[0])**2)+((pp0[1]-pp1[1])**2))
        return lenLine
    def lenghtContoureLine( contour, sort = True):
        lines = []
        for index in range(len(contour)-1):
            pointS = contour[index]
            pointE = contour[index+1]
            lenLine = sequencer.lenghtLine( pointS[0], pointE[0])
            pp0 = Point(pointS[0][0],pointS[0][1])
            pp1 = Point(pointE[0][0],pointE[0][1])
            dx = pp0.x-pp1.x
            dy = pp0.y-pp1.y
            lines.append((lenLine, pp0, pp1, dx, dy, index))
        if sort:
            lines = sorted(lines, key=lambda x: x[0], reverse=True)
        return lines

    def findParallelLines(approx):
        peri = cv2.arcLength(approx,False)/10
        lines = sequencer.lenghtContoureLine(approx)
        if len(lines)>3:
            lineA = lines[0]
            lineB = lines[1]
            lineC = lines[2]
            dxA = abs(lineA[1].x-lineA[2].x)
            dxB = abs(lineB[1].x-lineB[2].x)
            dxC = abs(lineC[1].x-lineC[2].x)
            x1 = sequencer.getMiddleX(lineA)
            x2 = sequencer.getMiddleX(lineB)
            x3 = sequencer.getMiddleX(lineC)
            border = 10
            if dxA < border and dxB < border  and dxC < border and lineA[0]>peri and lineB[0]>peri and lineC[0]>peri:
                xAll = [x1,x2, x3]
                xAll.sort()
                return True, xAll[0], xAll[1],xAll[2]
            if dxA < border and dxB  < border and lineA[0]>peri and lineB[0]>peri:
                xAll = [x1,x2]
                xAll.sort()
                return True, xAll[0], xAll[1], None
                # return True, lineA[1].x, lineB[1].x, None
        return False, None, None, None
    def getMiddleX(line):
        minX = min(line[1].x, line[2].x)
        x = minX + abs(line[1].x-line[2].x)/2
        return x
        # return line[1].x

    # крание и центральная нижняя точка
    def calk3PointRect(approx, lineN):
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

        return DirectionStatus.undifined
    