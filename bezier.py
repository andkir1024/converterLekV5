import enum
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
# from scipy import interpolate

class bezier:
    def is_eql(a_delta, b_delta, dist):
        if b_delta < dist and a_delta < dist:
            return True
        return False
    def is_eqlVal(a_val, b_val, dist):
        delta = (a_val - b_val)
        if delta < dist:
            return True
        return False
    # тестирование горизонтальные линии последовательно
    def testFig1(lineA, lineB, corner, path, dpi):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        xCenter = corner.minX + ((corner.maxX - corner.minX)/2)
        yCenter = corner.minY + ((corner.maxY - corner.minY)/2)
        # ab = LineString([Point(xCenter,corner.minY), Point(xCenter,corner.maxY)])
        # aaScaled  = bezier.resize_line(ab, ab.length * 2)
        # ab = LineString([Point(corner.minX,corner.minY), Point(xCenter,corner.minY)])
        # bc = LineString([Point(xCenter,corner.minY), Point(xCenter,yCenter)])
        # cd = LineString([Point(xCenter,yCenter), Point(xCenter,corner.maxY)])
        # de = LineString([Point(xCenter,corner.maxY),Point(corner.maxX,corner.maxY)]),

        deltaY = pp1.y-pp2.y
        coff0 = 0.5
        coff1 = 0.2
        if deltaY < 0:
            pA = Point(corner.minX,corner.minY)
            pB = Point(xCenter,corner.minY)
            pC = Point(xCenter,yCenter)
            pD = Point(xCenter,corner.maxY)
            pE = Point(corner.maxX,corner.maxY)

            path.L(pA.x / dpi, pA.y / dpi) 
            bezP1 = bezier.interpolatePoint(pA, pB, coff0)
            bezP2 = bezier.interpolatePoint(pB, pC, coff1)
            # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
            path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
            
            bezP1 = bezier.interpolatePoint(pC, pD, 0.8)
            bezP2 = bezier.interpolatePoint(pD, pE, 0.2)
            # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
            path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
        else:
            pA = Point(corner.minX,corner.maxY)
            pB = Point(xCenter,corner.maxY)
            pC = Point(xCenter,yCenter)
            pD = Point(xCenter,corner.minY)
            pE = Point(corner.maxX,corner.minY)

            path.L(pA.x / dpi, pA.y / dpi) 
            bezP1 = bezier.interpolatePoint(pA, pB, coff0)
            bezP2 = bezier.interpolatePoint(pB, pC, coff1)
            # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
            path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
            
            bezP1 = bezier.interpolatePoint(pC, pD, 0.8)
            bezP2 = bezier.interpolatePoint(pD, pE, 0.2)
            # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
            path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
        return True 
        '''
        pp0 = Point(lineA[1][0],lineA[1][1])
        pp3 = Point(lineB[0][0],lineB[0][1])

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

        path.L(pp0.x / dpi, pp0.y / dpi) 
        if doS:
            # сплине 0
            # path.L(tL.x / dpi, tL.y / dpi) 
            centroid1 = Point(xL,yS)
            centroid2 = Point(xL,yS)
            centroid2 = bezier.interpolatePoint(centroid2, tL, 0.1)
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tL.x / dpi, tL.y / dpi)
            
            # сплине 1 (center l)
            # path.L(tMain.x / dpi, tMain.y / dpi) 
            centroid1 = Point(xL,tMain.y)
            centroid2 = Point(xL,tMain.y)
            # centroid2 = CircuitSvg.interpolatePoint(centroid2, tMain, 0)
            centroid2 = bezier.interpolatePoint(centroid2, tMain, 0.4)
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tMain.x / dpi, tMain.y / dpi)
        
        if doReversS:
            # сплине 2 (center r)
            # path.L(tR.x / dpi, tR.y / dpi) 
            centroid1 = Point(xR,tMain.y)
            centroid2 = Point(xR,tMain.y)
            centroid1 = bezier.interpolatePoint(centroid1, tMain, 0.4)
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, tR.x / dpi, tR.y / dpi)

            # сплине 3
            # path.L(pp3.x / dpi, pp3.y / dpi) 
            centroid1 = Point(xR,yE)
            centroid2 = Point(xR,yE)
            centroid1 = bezier.interpolatePoint(centroid1, tR, 0.1)
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp3.x / dpi, pp3.y / dpi)
        '''
        return False    
    # тестирование вертикальые линии последовательно
    def testFig0(lineA, lineB, lineC, path, dpi):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        sY = pp1.y
        fY = pp2.y
        eqVert = bezier.is_eqlVal(sY, fY, 4)
        deltaY1 = pp1.y-pp0.y
        deltaY2 = pp3.y-pp2.y
        deltaX = pp1.x-pp2.x
        sign = deltaY1 * deltaY2
        if eqVert == True  and sign >= 0:
            if deltaX > 0:
                path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp1.y / dpi) 
            else:
                path.L(pp1.x / dpi, pp2.y / dpi).L(pp2.x / dpi, pp2.y / dpi) 
            # path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp1.y / dpi) 
            # path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp2.y / dpi) 
            return True
        return False    
    def createHalfCircleVer2(sA, fA, sB, fB, path, dpi, isLeft):
        # начальная и конечная точка кривой
        ab = LineString([fA, sB])
        cd_length = ab.length
        dir = 'left' 
        if isLeft == False:
            dir = 'right'
        # сдвиг на половину длины
        shiftedLine  = ab.parallel_offset(cd_length / 2, dir)
        shiftedLineScaled  = bezier.resize_line(shiftedLine, cd_length * 2)
        centroid = shiftedLineScaled.centroid
        #  part 0
        la=  LineString([sA, fA])
        coff0 = 0.5
        coff1 = 0.5
        laScaled  = bezier.resize_line(la, la.length * 2)
        result = shiftedLineScaled.intersection(laScaled)
        bezP1 = bezier.interpolatePoint(result, fA, coff0)
        bezP2 = bezier.interpolatePoint(result, centroid, coff1)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( centroid.x / dpi, centroid.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, centroid.x / dpi, centroid.y / dpi)
        
        #  part 1
        lb=  LineString([sB, fB])
        lbScaled  = bezier.resize_line(lb, lb.length * 2)
        result = shiftedLineScaled.intersection(lbScaled)
        bezP1 = bezier.interpolatePoint(result, centroid, coff1)
        bezP2 = bezier.interpolatePoint(result, sB, coff0)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( sB.x / dpi, sB.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, sB.x / dpi, sB.y / dpi)
        
        return

    # работа с овалами
    # закруглени sA, fA, sB, fB
    def get_angle(line: LineString) -> float:
        'Returns the angle (in radians) of a given line in relation with the X axis.'
        points = line.coords
            
        # start, end = line.boundary
        start, end = Point(points[0]),Point(points[1])
        if end.y - start.y == 0:  # Avoids dividing by zero.
            return math.acos(0)
        return -math.atan((end.x - start.x) / (end.y - start.y))

    def resize_line(line: LineString, length: float) -> LineString:
        'Returns a new line with the same center and angle of a given line, but with different length.'
        if len(line.coords) == 0:
            return None

        angle = bezier.get_angle(line)
        ext_x = round(length / 2 * math.sin(angle), 6)
        ext_y = round(length / 2 * math.cos(angle), 6)
        return LineString(([line.centroid.x + ext_x, line.centroid.y - ext_y],
                        [line.centroid.x - ext_x, line.centroid.y + ext_y]))

    def interpolatePoint(pointA, pointB, coff):
        line = LineString([pointA, pointB])
        length = line.length
        ip = line.interpolate(length * coff)
        return ip
    def divideLine(line, place):
        splitter = MultiPoint([line.interpolate((place), normalized=True) for i in range(1, 2)])
        split(line, splitter).wkt
        return splitter.centroid
    def convertToPoint(line):
        p0 = Point(line[0][0],line[0][1])
        p1 = Point(line[1][0],line[1][1])
        return p0, p1
    def aligmentHor(pp0, pp1):
        y = pp0.y + ((pp1.y - pp0.y)/2)
        return Point(pp0.x, y), Point(pp1.x, y)
    def aligmentVert(pp0, pp1):
        x = pp0.x + ((pp1.x - pp0.x)/2)
        return Point(x, pp0.y), Point(x, pp1.y)
    def is_parallel(line1, line2,minX,minY,maxX,maxY,linesFig ):
        a_delta_x = abs(line1[1][0] - line1[0][0])
        a_delta_y = abs(line1[1][1] - line1[0][1])
        b_delta_x = abs(line2[1][0] - line2[0][0])
        b_delta_y = abs(line2[1][1] - line2[0][1])
        '''
        # паралельность по вертикали
        eqVert = bezier.is_eql(a_delta_x, b_delta_x, 4)
        # паралельность по горизонтали
        eqHor = bezier.is_eql(a_delta_y, b_delta_y, 4)
        if eqHor == True:
            deltaX = line2[0][0] - line1[1][0]
            # начало второй правее конца первой (по горизонтали)
            # if line2[0][0] > line1[1][0]:
            #     # высота второй ниже высоты первой (по верикали)
            #     if line2[0][1] > line1[1][1]:
            #         return ParallStatus.hor_down
            #     else:
            #         return ParallStatus.hor_up
            # return ParallStatus.hor

        if eqVert == True:
            # return ParallStatus.vert
            # начало второй правее конца первой (по горизонтали)
            # if line2[0][0] > line1[1][0]:
            #     # высота второй ниже высоты первой (по верикали)
            #     if line2[0][1] > line1[1][1]:
            #         return ParallStatus.hor_down
            #     else:
            #         return ParallStatus.hor_up
            # return ParallStatus.hor

        # return ParallStatus.none
        '''        
