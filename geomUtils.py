import math
import cv2
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry
from shapely.ops import nearest_points

from commonData import DirectionStatus

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

    def directionCurveIntersectionV2(pp0, pp1, pp2, pp3, index):
        ab = LineString([pp0, pp1])
        bc = LineString([pp2, pp3])
        lenAB = ab.length
        lenBC = bc.length
        if lenAB > 500 or lenBC > 500:
            return False
        
        dx0 = abs (pp0.x - pp1.x)
        dy0 = abs (pp0.y - pp1.y)

        dy1 = abs (pp2.y - pp3.y)
        dx1 = abs (pp2.x - pp3.x)
        border = 10
        # if pp1.y > pp2.y and pp1.y > pp2.y and pp1.x > pp2.x:
        # if pp1.x > pp2.x:
        if dx0 < border and dy0 > border and dx1 > border and dy1 < border and pp0.y > pp2.y :
            return True
        if dx0 > border and dy0 < border and dx1 < border and dy1 > border and pp1.y < pp2.y :
            return True
        return False
    # расчет кривой безье для сглаженных углов
    def calkLineCurveIntersectionV2(cornerFig, pp0, pp1, pp2, pp3):
        pointsFig = cornerFig.pointsFig
        pp1a = Point(pp2.x, pp1.y)
        pp2a = Point(pp1.x, pp2.y)
        pp1a,pp2a=pp2a,pp1a

        tangent = LineString([pp1, pp2])

        points = []
        for point in pointsFig:
            points.append(point)
        ab = LineString([pp1a, pp2a])
        curve = LineString(points)
        result = curve.intersection(ab)
        resultSize = len(result.coords)
        if resultSize == 0:
            return None, None, None, None, None
        close = distance(tangent, result)
        p1, p2 = nearest_points(tangent, result)
        shiftedLine  = tangent.parallel_offset(close, "left")
        shiftedPoints  =shiftedLine.coords
        shiftedPoints0 = Point(shiftedPoints[0][0], shiftedPoints[0][1])
        shiftedPoints1 = Point(shiftedPoints[1][0], shiftedPoints[1][1])

        shiftedPoints0r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.4)
        shiftedPoints1r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.6)

        bezir0 = None 
        bezir1 = None 
        if pp1.x < pp2.x and pp1.y < pp2.y:
            pass
        elif pp1.x > pp2.x and pp1.y < pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp2a, 0.3)
            centroid1= bezier.interpolatePoint(pp2a, pp2, 0.7)
            bezir0 = Point(centroid0.x, pp1.y)
            bezir1 = Point(pp2.x, centroid1.y)
        elif pp1.x < pp2.x and pp1.y > pp2.y:
            pass
        elif pp1.x > pp2.x and pp1.y > pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp1a, 0.3)
            centroid1= bezier.interpolatePoint(pp1a, pp2, 0.7)
            bezir0 = Point(pp1.x, centroid0.y)
            bezir1 = Point(centroid1.x, pp2.y)
        else:
            pass

        return result, shiftedPoints0r, shiftedPoints1r, bezir0, bezir1

    def calkLineCurveIntersection(cornerFig, pp0, pp1, pp2, pp3):
        pointsFig = cornerFig.pointsFig
        pp1a = Point(pp2.x, pp1.y)
        pp2a = Point(pp1.x, pp2.y)

        tangent = LineString([pp1, pp2])
        centroid = tangent.centroid

        points = []
        for point in pointsFig:
            points.append(point)
        ab = LineString([pp1a, pp2a])
        curve = LineString(points)
        result = curve.intersection(ab)
        resultSize = len(result.coords)
        if resultSize == 0:
            return None, None, None, None, None
        close = distance(tangent, result)
        p1, p2 = nearest_points(tangent, result)
        shiftedLine  = tangent.parallel_offset(close, "right")
        shiftedPoints  =shiftedLine.coords
        shiftedPoints0 = Point(shiftedPoints[0][0], shiftedPoints[0][1])
        shiftedPoints1 = Point(shiftedPoints[1][0], shiftedPoints[1][1])

        shiftedPoints0r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.4)
        shiftedPoints1r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.6)
        # shiftedPoints0r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.45)
        # shiftedPoints1r = bezier.interpolatePoint(shiftedPoints0, shiftedPoints1, 0.55)

        
        # # bezir0 = Point(abs(pp1.x + abs(pp1a.x-pp1.x)/2), pp1a.y)
        # bezir0 = Point(abs(min(pp1a.x, pp1.x) + abs(pp1a.x-pp1.x)/2), pp1a.y)
        # bezir1 = Point(pp2.x, abs(pp2.y - abs(pp2.y-pp1.y)/2))

        # bezir0 = Point(abs(min(pp1a.x, pp1.x) + abs(pp1a.x-pp1.x)/2), pp1a.y)
        # bezir1 = Point(pp2.x, abs(pp2.y - abs(pp2.y-pp1.y)/2))

        if pp1.x < pp2.x and pp1.y < pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp1a, 0.3)
            centroid1= bezier.interpolatePoint(pp1a, pp2, 0.7)
            bezir0 = Point(centroid0.x, pp1.y)
            bezir1 = Point(pp2.x, centroid1.y)
            # bezir0 = Point(centroid.x, pp1.y)
            # bezir1 = Point(pp2.x, centroid.y)
        elif pp1.x > pp2.x and pp1.y < pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp2a, 0.3)
            centroid1= bezier.interpolatePoint(pp2a, pp2, 0.7)
            bezir0 = Point(pp1.x, centroid0.y)
            bezir1 = Point(centroid1.x, pp2.y)
            # bezir0 = Point(pp1.x, centroid.y)
            # bezir1 = Point(centroid.x, pp2.y)
        elif pp1.x < pp2.x and pp1.y > pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp2a, 0.3)
            centroid1= bezier.interpolatePoint(pp2a, pp2, 0.7)
            bezir0 = Point(pp1.x, centroid0.y)
            bezir1 = Point(centroid1.x, pp2.y)
            # bezir0 = Point(pp1.x, centroid.y)
            # bezir1 = Point(centroid.x, pp2.y)
        elif pp1.x > pp2.x and pp1.y > pp2.y:
            centroid0= bezier.interpolatePoint(pp1, pp1a, 0.3)
            centroid1= bezier.interpolatePoint(pp1a, pp2, 0.7)
            bezir0 = Point(centroid0.x, pp1.y)
            bezir1 = Point(pp2.x, centroid1.y)
        else:
            pass
        
            # bezir0 = Point(centroid.x, pp1.y)
            # bezir1 = Point(pp2.x, centroid.y)

        return result, shiftedPoints0r, shiftedPoints1r, bezir0, bezir1

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

    # прверка является ли соединение последовательной гоизонтальной линией
    def checkHorizont(lineA, lineB):
        dxA = abs(lineA[0][0]-lineA[1][0])
        dyA = abs(lineA[0][1]-lineA[1][1])
        lenA = geometryUtils.lenghtLineConture(lineA)

        dxB = abs(lineB[0][0]-lineB[1][0])
        dyB = abs(lineB[0][1]-lineB[1][1])
        lenB = geometryUtils.lenghtLineConture(lineB)
        if lenA < 100 or lenB < 100:
            return False

        border = 15
        if dyA < border and dyB < border:
            if abs(lineB[0][0] - lineA[1][0]) > 0:
                return True
        return False
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

        border = 15
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
