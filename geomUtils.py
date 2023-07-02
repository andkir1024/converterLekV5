import math
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry

class geometryUtils:
    def centerLine(line):
        pointS = Point(line[0][0], line[0][1])
        pointE = Point(line[1][0], line[1][1])
        xCenter = pointS.x + ((pointE.x - pointS.x)/2)
        yCenter = pointS.y + ((pointE.y - pointS.y)/2)
        return Point(xCenter, yCenter)
    
    def centerConnectionLines(lineA, lineB):
        pointS = Point(lineA[1][0], lineA[1][1])
        pointE = Point(lineB[0][0], lineB[0][1])
        xCenter = pointS.x + ((pointE.x - pointS.x)/2)
        yCenter = pointS.y + ((pointE.y - pointS.y)/2)
        return Point(xCenter, yCenter)

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

    def converterLineToPoints( lineA, lineB):
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])
        return pp0,pp1,pp2,pp3
    
    def lenghtLine( pp0, pp1):
        lenLine = math.sqrt( ((pp0[0]-pp1[0])**2)+((pp0[1]-pp1[1])**2))
        return lenLine
    def lenghtLineConture( line):
        dxA = abs(line[0][0]-line[1][0])
        dyA = abs(line[0][1]-line[1][1])
        lenLine = math.sqrt( (dxA**2)+(dyA**2))
        return lenLine
    def lenghtContoureLine( contour):
        maxVal =0
        pp0 = Point(0,0)
        pp1 = Point(0,0)
        for index in range(len(contour)-1):
            pointS = contour[index]
            pointE = contour[index+1]
            lenLine = geometryUtils.lenghtLine( pointS[0], pointE[0])
            if lenLine> maxVal:
                maxVal = lenLine
                pp0 = Point(pointS[0][0],pointS[0][1])
                pp1 = Point(pointE[0][0],pointE[0][1])
        return maxVal, pp0, pp1

    def calkPointIntersection(pointAstart, pointAend, pointBstart, pointBend):
        pp0s, pp1s = geometryUtils.scale(pointAstart, pointAend, 30)
        pp2s, pp3s = geometryUtils.scale(pointBstart, pointBend, 30)
        l1 = LineString([pp0s, pp1s])
        l2 = LineString([pp2s, pp3s])
        result = l1.intersection(l2)
        size = len(result.coords)
        if size == 0:
            return None
        return result

    # прверка является ли соединение линий углом
    def checkCorner(lineA, lineB):
        dxA = abs(lineA[0][0]-lineA[1][0])
        dyA = abs(lineA[0][1]-lineA[1][1])
        lenA = geometryUtils.lenghtLineConture(lineA)

        dxB = abs(lineB[0][0]-lineB[1][0])
        dyB = abs(lineB[0][1]-lineB[1][1])
        lenB = geometryUtils.lenghtLineConture(lineB)
        if lenA < 100 or lenB < 100:
            return False

        border = 10
        if dyA < border and dxB < border:
            return True
        if dxA < border and dyB < border:
            return True
        if dyA < border and dxB < border:
            return True
        if dxA < border and dyB < border:
            return True
        return False

    # прверка является ли соединение нижним вырезом
    def checkDownU(lineA, lineB):
        dxA = abs(lineA[0][0]-lineA[1][0])
        dyA = abs(lineA[0][1]-lineA[1][1])
        lenA = geometryUtils.lenghtLineConture(lineA)

        dxB = abs(lineB[0][0]-lineB[1][0])
        dyB = abs(lineB[0][1]-lineB[1][1])
        lenB = geometryUtils.lenghtLineConture(lineB)
        if lenA < 100 or lenB < 100:
            return False

        dyAB0 = abs(lineA[0][1]-lineB[1][1])
        dyAB1 = abs(lineB[0][1]-lineA[1][1])

        border = 30
        if dxA < border and dxB < border:
            if dyAB0 < border and dyAB1 < border:
                return True
        return False
