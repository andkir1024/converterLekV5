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

from bezier import bezier, contoureAnalizer, FigureStatus

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

# class CornerStatus(enum.Enum):
#     # закругленный угол
#     round = 0
#     # последовательность линий
#     lineStrip = 1

class LineStatus(enum.Enum):
    round = 0
    sequest = 1
    parallel = 2
    undefined = 3

class Corner:
    cross = ParallStatus.none
    minX = minY =maxX =maxY=0
    linesFig = None
    pointsFig = None
    def __init__(self, minX,minY,maxX,maxY,linesFig,cross, pointsFig):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.cross = cross
        self.linesFig = linesFig
        self.pointsFig = pointsFig

class CircuitSvg:
    
    def createContureSvg(lines, draw, path, dpi):
        indexMax = len(lines)-1
        # добавление горизонтального овала 
        if indexMax == 1:
            lineA = lines[0]
            lineB = lines[1]

            pp0, pp1 = bezier.convertToPoint(lineA)
            pp2, pp3 = bezier.convertToPoint(lineB)
            
            pp0, pp1 = bezier.aligmentHor(pp0, pp1)
            pp2, pp3 = bezier.aligmentHor(pp2, pp3)
            
            pp1, pp2 = bezier.aligmentVert(pp1, pp2)
            pp0, pp3 = bezier.aligmentVert(pp0, pp3)

            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            bezier.createHalfCircleVer2(pp0, pp1, pp2, pp3, path, dpi, False)
            path.L(pp2.x / dpi, pp2.y / dpi).L(pp3.x / dpi, pp3.y / dpi) 
            bezier.createHalfCircleVer2(pp2, pp3, pp0, pp1, path, dpi, False)
            path.Z()
            draw.append(path)
            return

        # добавление главного контура
        contoureAnalizer.start()
        
        # '''
        typeFigures = []
        typeFigures.append(contoureAnalizer.drawCountureFromLine(lines[indexMax],lines[0]))
        for index in range(indexMax):
            typeFigures.append(contoureAnalizer.drawCountureFromLine(lines[index],lines[index+1]))

        pp0, pp1 = CircuitSvg.getStartPoint(lines[indexMax][0], lines[indexMax][1],lines[0][0], lines[0][1])
        path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
        for index in range(len(typeFigures)):
            if typeFigures[index][0] == FigureStatus.smoothCorner:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                CircuitSvg.doLekaloCorner(lineA, lineB, path, dpi, False)
                continue
            if typeFigures[index][0] == FigureStatus.halfCircleUp:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]

                corner = lineA[6]
                pp0 = Point(lineA[1][0],lineA[1][1])
                pp1 = Point(lineA[1][0],lineA[1][1])
                pp2 = Point(lineB[0][0],lineA[1][1])
                pp2 = Point(corner.minX + ((corner.maxX - corner.minX)/2),corner.minY)
                pp3 = Point(lineB[0][0],lineB[0][1])
                
                path.L(pp0.x / dpi, pp0.y / dpi) 
                CircuitSvg.createHalfCircle(lineA, lineB, path, dpi, True)                
                continue
            if typeFigures[index][0] == FigureStatus.sUpDown:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                xCenter,yCenter,deltaX,prop = bezier.prepareS(lineA, lineB, corner)
                if deltaX < 0:
                    bezier.doSUpDown(xCenter,yCenter, corner, path, dpi, 0.6, 0.9, True,prop)
                else:
                    bezier.doSUpDown(xCenter,yCenter, corner, path, dpi, 0.5, 0.2,False,prop)
                continue
            if typeFigures[index][0] == FigureStatus.sDownUp:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                xCenter,yCenter,deltaX,prop = bezier.prepareS(lineA, lineB, corner)
                if deltaX < 0:
                    bezier.doSDownUp(xCenter,yCenter, corner, path, dpi, 0.6, 0.9, True,prop)
                    # bezier.doSDownUp(xCenter,yCenter, corner, path, dpi, 0.5, 0.2, True,prop)
                else:
                    bezier.doSDownUp(xCenter,yCenter, corner, path, dpi, 0.5, 0.2, False,prop)
                continue
            if typeFigures[index][0] == FigureStatus.cutoutRect:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                
                bezier.doCutoutTriangle(lineA,lineB, corner, path, dpi, True)
                continue
            if typeFigures[index][0] == FigureStatus.cutoutTriangle:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                
                bezier.doCutoutTriangle(lineA,lineB, corner, path, dpi, False)
                continue
            if typeFigures[index][0] == FigureStatus.camelA:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                
                bezier.doCamel(lineA,lineB, corner, path, dpi, FigureStatus.camelA)
                continue
            if typeFigures[index][0] == FigureStatus.camelB:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                
                bezier.doCamelB(lineA,lineB, corner, path, dpi)
                continue
            if typeFigures[index][0] == FigureStatus.camelC:
                lineA = typeFigures[index][1]
                lineB = typeFigures[index][2]
                corner = lineA[6]
                
                bezier.doCamelC(lineA,lineB, corner, path, dpi)
                continue
            
        
        '''
        pp0, pp1, centroid1, centroid2, pp2 = CircuitSvg.createAngle(lines[indexMax][0], lines[indexMax][1],lines[0][0], lines[0][1])
        if pp0 is not None:
            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            ctartCorner = CircuitSvg.doLekaloCorner(lines[indexMax], lines[0], path, dpi, True)
            # path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
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
                deltaX = abs(lineB[0][0] - lineA[1][0])
                deltaY = abs(lineB[0][1] - lineA[1][1])
                if deltaY >10:
                    # гор - гор - гор
                    # continue
                    isFig1 = bezier.testFig1(lineA,lineB, corner, path, dpi)
                else:
                    isFig1 = bezier.testFig2(lineA,lineB, corner, path, dpi)
                continue
            if corner.cross == ParallStatus.vert:
                isFig0 = bezier.testFig0(lineA,lineB, lineC, path, dpi)
                if isFig0 == True:
                    continue
                else:
                    pp0 = Point(lineA[1][0],lineA[1][1])
                    pp1 = Point(lineA[1][0],lineA[1][1])
                    pp2 = Point(lineB[0][0],lineA[1][1])
                    pp2 = Point(corner.minX + ((corner.maxX - corner.minX)/2),corner.minY)
                    pp3 = Point(lineB[0][0],lineB[0][1])
                    
                    path.L(pp0.x / dpi, pp0.y / dpi) 
                    CircuitSvg.createHalfCircle(lineA, lineB, path, dpi, True)                
                continue
            else:
                CircuitSvg.doLekaloCorner(lineA, lineB, path, dpi, False)
            '''                

                
        path.Z()
        draw.append(path)
        return
    # создание углов главного контура лекала
    def doLekaloCorner(lineA, lineB, path , dpi, start):
        # contoureAnalizer.drawCountureFromLine(lineA)
        idSmoth = CircuitSvg.createCornerLine(lineA[6].pointsFig, path, dpi)
        if idSmoth == True:
            pp0, pp1, centroid1, centroid2, pp2 = CircuitSvg.createAngle(lineA[0], lineA[1],lineB[0], lineB[1])
            if pp0 is not None:
                path.L(pp1.x / dpi, pp1.y / dpi) 
                path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
                return True
            else:
                return False
        return True

    def createCornerLine(points, path , dpi):
        peri = cv2.arcLength(points,True)
        # approx = cv2.approxPolyDP(points, 0.02 * peri, False)
        approx = cv2.approxPolyDP(points, 0.05 * peri, False)
        if approx.size == 4: 
            st = approx[0]
            x1,y1 = st[:, 0][0],st[:, 1][0]
            fin = approx[1]
            x2,y2 = fin[:, 0][0],fin[:, 1][0]
            # x1,y1 = points[0][0],points[0][1]
            # x2,y2 = points[-1][0],points[-1][1]
            
            path.L(x2/dpi,y2/dpi) 
            path.L(x1/dpi,y1/dpi) 
            return False
        return True
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
        pointA0, pointA1 = bezier.convertToPoint(lineA)

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
    
    def getStartPoint(pointA, pointB,pointC, pointD):
        distAC = CircuitSvg.distancePoint(pointA, pointC) 
        distAD = CircuitSvg.distancePoint(pointA, pointD)
        distBC = CircuitSvg.distancePoint(pointB, pointC)
        distBD = CircuitSvg.distancePoint(pointB, pointD)
        
        a = np.array([distAC,distAD,distBC,distBD])
        index = np.where(a == a.min())[0][0]
        point0 = None
        point1 = None
        if index == 1:
            point0 = pointB
            point1 = pointA
        elif index == 2:
            point0 = pointA
            point1 = pointB
        elif index == 0:
            point0 = pointA
            point1 = pointB
        else:
            zz=0
            
        pp0 = Point(point0[0],point0[1])
        pp1 = Point(point1[0],point1[1])
        return pp0, pp1
    