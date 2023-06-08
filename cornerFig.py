import enum
import cv2
import numpy as np
import math
import drawsvg as drawSvg
# from drawUtils import LineStatus, cvDraw

from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split

from bezier import bezier

# статус паралельных линий
class ParallStatus(enum.Enum):
    # не паралельны
    none = 0
    # закругленный угол
    vert = 1
    vert_left = 2
    vert_right = 3
    # последовательность линий
    hor_down = 4
    hor_up = 5
    hor = 6
    def isCoord(stat):
        if stat == ParallStatus.none:
            return False
        if stat == ParallStatus.vert or stat == ParallStatus.vert_left or stat == ParallStatus.vert_right:
            return False
        if stat == ParallStatus.hor_down or stat == ParallStatus.hor_up or stat == ParallStatus.hor:
            return False
        return True

class CornerStatus(enum.Enum):
    # закругленный угол
    round = 0
    # последовательность линий
    lineStrip = 1

class LineStatus(enum.Enum):
    round = 0
    sequest = 1
    parallel = 2
    undefined = 3

class Corner:
    cross = ParallStatus.none
    minX = minY =maxX =maxY=0
    linesFig = None
    def __init__(self, minX,minY,maxX,maxY,linesFig,cross):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.cross = cross
        self.linesFig = linesFig

class CircuitSvg:
    def aligmentHor(pp0, pp1):
        y = pp0.y + ((pp1.y - pp0.y)/2)
        return Point(pp0.x, y), Point(pp1.x, y)
    def aligmentVert(pp0, pp1):
        x = pp0.x + ((pp1.x - pp0.x)/2)
        return Point(x, pp0.y), Point(x, pp1.y)
    def createContureSvg(lines, draw, path, dpi):
        indexMax = len(lines)-1
        # добавление горизонтального овала 
        if indexMax == 1:
            lineA = lines[0]
            lineB = lines[1]

            pp0, pp1 = CircuitSvg.convertToPoint(lineA)
            pp2, pp3 = CircuitSvg.convertToPoint(lineB)
            
            pp0, pp1 = CircuitSvg.aligmentHor(pp0, pp1)
            pp2, pp3 = CircuitSvg.aligmentHor(pp2, pp3)
            
            pp1, pp2 = CircuitSvg.aligmentVert(pp1, pp2)
            pp0, pp3 = CircuitSvg.aligmentVert(pp0, pp3)

            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            bezier.createHalfCircleVer2(pp0, pp1, pp2, pp3, path, dpi, False)
            path.L(pp2.x / dpi, pp2.y / dpi).L(pp3.x / dpi, pp3.y / dpi) 
            bezier.createHalfCircleVer2(pp2, pp3, pp0, pp1, path, dpi, False)
            path.Z()
            draw.append(path)
            return

        # добавление главного контура
        pp0, pp1, centroid1, centroid2, pp2 = CircuitSvg.createAngle(lines[indexMax][0], lines[indexMax][1],lines[0][0], lines[0][1])
        if pp0 is not None:
            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
        else:
            lineA = lines[0]
            lineB = lines[indexMax]
            path.M(lineA[0][0] / dpi, lineA[0][1] / dpi)

        for index in range(indexMax):
            lineA = lines[index]
            lineB = lines[index+1]
            lineC = None
            if index < indexMax - 2:
                lineC = lines[index+2]
                
            typeLine = lineA[2]
            corner = lineA[6]
            width = corner.maxX-corner.minX
            height = corner.maxY-corner.minY
            if corner.cross == ParallStatus.hor:
                pp0 = Point(lineA[1][0],lineA[1][1])
                # pp1 = Point(lineA[1][0],corner.maxY)
                # pp2 = Point(lineB[0][0],corner.maxY)
                pp3 = Point(lineB[0][0],lineB[0][1])
                # path.L(pp0.x / dpi, pp0.y / dpi) 
                # path.L(pp1.x / dpi, pp1.y / dpi) 
                # path.L(pp2.x / dpi, pp2.y / dpi) 
                # path.L(pp3.x / dpi, pp3.y / dpi) 

                xS = lineA[1][0]
                xCenter = corner.minX + ((corner.maxX - corner.minX)/2)
                xL = corner.minX + ((xCenter - corner.minX)/2)
                xR = xCenter + ((xCenter - corner.minX)/2)
                xE = lineB[0][0]
                
                deltaY = lineA[1][1] - lineB[0][1]
                doReversS = True
                doS = True
                if abs(deltaY) > 5:
                    if deltaY > 5:
                        doS = False
                    else:
                        doReversS = False

                yS = lineA[1][1]
                yCenter = corner.minY + ((corner.maxY - corner.minY)/2)
                yE = lineB[0][1]

                tL = Point(xL,yCenter)
                tMain = Point(xCenter,corner.maxY)
                tR = Point(xR,yCenter)

                # pp1 = Point(lineA[1][0],corner.maxY)
                # pp2 = Point(lineB[0][0],corner.maxY)
                # pp3 = Point(lineB[0][0],lineB[0][1])
                path.L(pp0.x / dpi, pp0.y / dpi) 
                if doS:
                    # сплине 0
                    # path.L(tL.x / dpi, tL.y / dpi) 
                    centroid1 = Point(xL,yS)
                    centroid2 = Point(xL,yS)
                    centroid2 = CircuitSvg.interpolatePoint(centroid2, tL, 0.1)
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tL.x / dpi, tL.y / dpi)
                    
                    # сплине 1 (center l)
                    # path.L(tMain.x / dpi, tMain.y / dpi) 
                    centroid1 = Point(xL,tMain.y)
                    centroid2 = Point(xL,tMain.y)
                    # centroid2 = CircuitSvg.interpolatePoint(centroid2, tMain, 0)
                    centroid2 = CircuitSvg.interpolatePoint(centroid2, tMain, 0.4)
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tMain.x / dpi, tMain.y / dpi)
                
                if doReversS:
                    # сплине 2 (center r)
                    # path.L(tR.x / dpi, tR.y / dpi) 
                    centroid1 = Point(xR,tMain.y)
                    centroid2 = Point(xR,tMain.y)
                    centroid1 = CircuitSvg.interpolatePoint(centroid1, tMain, 0.4)
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tR.x / dpi, tR.y / dpi)

                    # сплине 3
                    # path.L(pp3.x / dpi, pp3.y / dpi) 
                    centroid1 = Point(xR,yE)
                    centroid2 = Point(xR,yE)
                    centroid1 = CircuitSvg.interpolatePoint(centroid1, tR, 0.1)
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp3.x / dpi, pp3.y / dpi)
                continue
            if corner.cross == ParallStatus.vert:
                isFig0 = bezier.testFig0(lineA,lineB, lineC)
                pp0 = Point(lineA[1][0],lineA[1][1])
                # pp1 = Point(lineA[1][0],corner.minY)
                # pp2 = Point(lineB[0][0],corner.minY)

                pp1 = Point(lineA[1][0],lineA[1][1])
                pp2 = Point(lineB[0][0],lineA[1][1])
                pp2 = Point(corner.minX + ((corner.maxX - corner.minX)/2),corner.minY)
                pp3 = Point(lineB[0][0],lineB[0][1])
                
                path.L(pp0.x / dpi, pp0.y / dpi) 
                
                # path.L(pp1.x / dpi, pp1.y / dpi) 
                # path.L(pp2.x / dpi, pp2.y / dpi) 
                # path.L(pp3.x / dpi, pp3.y / dpi) 
                
                CircuitSvg.createHalfCircle(lineA, lineB, path, dpi, True)                
                continue
            # if typeLine == LineStatus.sequest:
            #     path.L(lineB[1][0] / dpi,lineB[1][1] / dpi) 
            #     continue
            # elif typeLine == LineStatus.parallel:
            #     CircuitSvg.createHalfCircle(lineA, lineB, path, dpi, True)
            #     continue
            else:
                pp0, pp1, centroid1, centroid2, pp2 = CircuitSvg.createAngle(lineA[0], lineA[1],lineB[0], lineB[1])
                if pp0 is not None:
                    path.L(pp1.x / dpi, pp1.y / dpi) 
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
        path.Z()
        draw.append(path)
        return
    
    def convertToPoint(line):
        p0 = Point(line[0][0],line[0][1])
        p1 = Point(line[1][0],line[1][1])
        return p0, p1
    def convertToLineString(line):
        pointA = line[0]
        pointB = line[1]
        startCur = Point(pointA[0],pointA[1])
        finCur = Point(pointB[0],pointB[1])
        ab = LineString([startCur, finCur])
        return ab

    def createSFigure(lineA, lineB, path, dpi, isLeft):
        pointA = lineA[1]
        pointB = lineB[0]
        cd_length = CircuitSvg.distancePoint(pointA, pointB)
        
        # начальная и конечная точка кривой
        startCur = Point(pointA[0],pointA[1])
        finCur = Point(pointB[0],pointB[1])
        ab = LineString([startCur, finCur])
        dir = 'left'
        if isLeft == False:
            dir = 'right'
        # сдвиг на половину длины
        shiftedLine  = ab.parallel_offset(cd_length / 2, dir)
                                    
        centroid = shiftedLine.centroid.coords
        xCenter = centroid[0][0]
        yCenter = centroid[0][1]
        # получение контрольных точек для кривой безье
        
        bezP1, bezP2 = CircuitSvg.calkControlPoints(lineA, shiftedLine, 0.01)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, xCenter / dpi, yCenter / dpi)

        bezP1, bezP2 = CircuitSvg.calkControlPoints(lineB, shiftedLine, 0.01)
        path.C(bezP2.x / dpi, bezP2.y / dpi, bezP1.x / dpi, bezP1.y / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        # path.C(start[0] / dpi, start[1] / dpi, start[0] / dpi, start[1] / dpi, xCenter / dpi, yCenter / dpi)
        # path.C(fin[0] / dpi, fin[1] / dpi, fin[0] / dpi, fin[1] / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        return
    def createHalfCircle(lineA, lineB, path, dpi, isLeft):
        pointA = lineA[1]
        pointB = lineB[0]
        cd_length = CircuitSvg.distancePoint(pointA, pointB)
        
        # начальная и конечная точка кривой
        startCur = Point(pointA[0],pointA[1])
        finCur = Point(pointB[0],pointB[1])
        ab = LineString([startCur, finCur])
        dir = 'left'
        if isLeft == False:
            dir = 'right'
        # сдвиг на половину длины
        shiftedLine  = ab.parallel_offset(cd_length / 2, dir)
                                    
        centroid = shiftedLine.centroid.coords
        size = len(centroid)
        if size == 0:
            return
        
        xCenter = centroid[0][0]
        yCenter = centroid[0][1]
        # получение контрольных точек для кривой безье
        
        bezP1, bezP2 = CircuitSvg.calkControlPoints(lineA, shiftedLine, 0.101)
        if bezP1 is None:
            return
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, xCenter / dpi, yCenter / dpi)

        bezP1, bezP2 = CircuitSvg.calkControlPoints(lineB, shiftedLine, 0.101)
        if bezP1 is None:
            return
        path.C(bezP2.x / dpi, bezP2.y / dpi, bezP1.x / dpi, bezP1.y / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        # path.C(start[0] / dpi, start[1] / dpi, start[0] / dpi, start[1] / dpi, xCenter / dpi, yCenter / dpi)
        # path.C(fin[0] / dpi, fin[1] / dpi, fin[0] / dpi, fin[1] / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        return
    # вычисление контрольных точек для безье
    def calkControlPoints(lineA, lineB, place):
        pointA0, pointA1 = CircuitSvg.convertToPoint(lineA)

        pp0s, pp1s = CircuitSvg.scale(pointA0, pointA1, 30)
        coordsB = lineB.coords
        pp2s, pp3s = CircuitSvg.scale(Point(coordsB[0][0],coordsB[0][1]), Point(coordsB[1][0],coordsB[1][1]), 30)
        l1 = LineString([pp0s, pp1s])
        l2 = LineString([pp2s, pp3s])
        # пересечение линий
        result = l1.intersection(l2)
        size = len(result.coords)
        if size == 0:
            return None, None

        lineResult1 = CircuitSvg.createLineFromInterction(pointA0,pointA1,result)
        # lineResult1 = lineResult1.centroid

        lineResult2 = CircuitSvg.createLineFromInterction(coordsB[0],coordsB[1],result)
        # return lineResult1.centroid, result
        
        bez0= bezier.divideLine(lineResult1, 0.101)
        bez1= bezier.divideLine(lineResult2, 0.101)
        return bez0, bez1
    def distancePoint(pointA, pointB):
        deltaX = pointA[0]-pointB[0]
        deltaY = pointA[1]-pointB[1]
        lenLine = math.sqrt( (deltaX**2)+(deltaY**2))
        return lenLine
    def scale(firstPoint, secondPoint, factor):
        t0=0.5*(1.0-factor)
        t1=0.5*(1.0+factor)
        x1 = firstPoint.x +(secondPoint.x - firstPoint.x) * t0
        y1 = firstPoint.y +(secondPoint.y - firstPoint.y) * t0
        x2 = firstPoint.x +(secondPoint.x - firstPoint.x) * t1
        y2 = firstPoint.y +(secondPoint.y - firstPoint.y) * t1

        firstPoint = Point(x1, y1)
        secondPoint = Point(x2, y2)
        return firstPoint, secondPoint
    def createLineFromInterction(pointA, pointB, intersectionPoint):
        l1 = LineString([pointA, intersectionPoint])
        l2 = LineString([pointB, intersectionPoint])
        l1length = l1.length
        l2length = l2.length
        if l2length < l1length:
            return l2
        return l1
    # работа с контуром
    # создание зхакругления для контура
    # если Nont то паралельны
    def createAngle(pointA, pointB,pointC, pointD):
        distAC = CircuitSvg.distancePoint(pointA, pointC) 
        distAD = CircuitSvg.distancePoint(pointA, pointD)
        distBC = CircuitSvg.distancePoint(pointB, pointC)
        distBD = CircuitSvg.distancePoint(pointB, pointD)
        
        a = np.array([distAC,distAD,distBC,distBD])
        index = np.where(a == a.min())[0][0]
        point0 = None
        point1 = None
        point2 = None
        point3 = None
        if index == 1:
            point0 = pointB
            point1 = pointA
            point2 = pointD
            point3 = pointC
        elif index == 2:
            point0 = pointA
            point1 = pointB
            point2 = pointC
            point3 = pointD
        elif index == 0:
            point0 = pointA
            point1 = pointB
            point2 = pointC
            point3 = pointD
        else:
            zz=0
            
        pp0 = Point(point0[0],point0[1])
        pp1 = Point(point1[0],point1[1])
        pp2 = Point(point2[0],point2[1])
        pp3 = Point(point3[0],point3[1])
        
        pp0s, pp1s = CircuitSvg.scale(pp0, pp1, 30)
        pp2s, pp3s = CircuitSvg.scale(pp2, pp3, 30)

        l1 = LineString([pp0s, pp1s])
        l2 = LineString([pp2s, pp3s])
        result = l1.intersection(l2)
        testOut = str(result)
        if testOut.find("EMPTY") >= 0 or testOut.find("LINE") >= 0:
            return None, None, None, None, None

        # poly = Polygon([pp0,pp1,pp2,pp3])
        # containt = poly.contains(result)
        # if containt == False:
        #     return None, None, None, None, None
        # boundary = poly.boundary
        
        l3 = LineString([pp1, result])
        l4 = LineString([pp2, result])

        centroid1 = l3.centroid
        centroid2 = l4.centroid
        return pp0, pp1, centroid1, centroid2, pp2
    