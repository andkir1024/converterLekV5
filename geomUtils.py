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
    
        # distAC = CircuitSvg.distancePoint(pointA, pointC) 
        # distAD = CircuitSvg.distancePoint(pointA, pointD)
        # distBC = CircuitSvg.distancePoint(pointB, pointC)
        # distBD = CircuitSvg.distancePoint(pointB, pointD)
        
        # a = np.array([distAC,distAD,distBC,distBD])
        # index = np.where(a == a.min())[0][0]
        # point0 = None
        # point1 = None
        # point2 = None
        # point3 = None
        # if index == 1:
        #     point0 = pointB
        #     point1 = pointA
        #     point2 = pointD
        #     point3 = pointC
        # elif index == 2:
        #     point0 = pointA
        #     point1 = pointB
        #     point2 = pointC
        #     point3 = pointD
        # elif index == 0:
        #     point0 = pointA
        #     point1 = pointB
        #     point2 = pointC
        #     point3 = pointD
        # else:
        #     zz=0
            
        # pp0 = Point(point0[0],point0[1])
        # pp1 = Point(point1[0],point1[1])
        # pp2 = Point(point2[0],point2[1])
        # pp3 = Point(point3[0],point3[1])
        
        # pp0s, pp1s = CircuitSvg.scale(pp0, pp1, 30)
        # pp2s, pp3s = CircuitSvg.scale(pp2, pp3, 30)

        # l1 = LineString([pp0s, pp1s])
        # l2 = LineString([pp2s, pp3s])
        # result = l1.intersection(l2)
        # testOut = str(result)
        # if testOut.find("EMPTY") >= 0 or testOut.find("LINE") >= 0:
        #     return None, None, None, None, None

        
        # l3 = LineString([pp1, result])
        # l4 = LineString([pp2, result])

        # centroid1 = l3.centroid
        # centroid2 = l4.centroid
        # return pp0, pp1, centroid1, centroid2, pp2

