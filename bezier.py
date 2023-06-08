import enum
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from scipy import interpolate

class bezier:
    # тестирование вертикальые линии последовательно
    def testFig0(lineA, lineB, lineС):
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
