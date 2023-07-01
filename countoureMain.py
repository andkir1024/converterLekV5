import enum

import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry

class svgCountoure(enum.Enum):
    svgM = 0
    svgL = 1
    svgC = 2
    svgZ = 3
class svgPath:
    svg = []
    def __init__(self):
        self.data = []
    def addM(self, pp):
        param= (svgCountoure.svgM, pp)
        self.svg.append(param)
        return
    def addL(self, pp):
        param= (svgCountoure.svgL, pp)
        self.svg.append(param)
        return
    def addZ(self):
        param= (svgCountoure.svgZ, None)
        self.svg.append(param)
        return
    def addC(self, pp0, pp1, pp2, pp3):
        bezP1, bezP2, centroid, bezP3, bezP4, sB = bezier.createHalfCircle(pp0, pp1, pp2, pp3)
        
        param= (svgCountoure.svgC, bezP1, bezP2, centroid, bezP3, bezP4, sB)
        self.svg.append(param)
        return        
    def doPath(self, path, dpi):
        for item in self.svg:
            if item[0] == svgCountoure.svgM:
                path.M(item[1].x / dpi, item[1].y / dpi)
            if item[0] == svgCountoure.svgL:
                path.L(item[1].x / dpi, item[1].y / dpi)
            if item[0] == svgCountoure.svgZ:
                path.Z()
            if item[0] == svgCountoure.svgC:
                path.C(item[1].x / dpi, item[1].y / dpi, item[2].x / dpi, item[2].y / dpi, item[3].x / dpi, item[3].y / dpi)
                path.C(item[4].x / dpi, item[4].y / dpi, item[5].x / dpi, item[5].y / dpi, item[6].x / dpi, item[6].y / dpi)
        return
    def createFlatCouture(self, lines):
        for index in range(len(lines)):
            line = lines[index]
            pp0, pp1 = bezier.convertToPoint(line)
            if index == 0:
                self.addM(pp0)
            else:
                self.addL(pp0)
            self.addL(pp1)
        self.addZ()
    def testPointInCounture(self, lines, circles):
        circlesNew = []
        points=[]
        for pp in lines:
            point = Point(pp[0][0], pp[0][1])
            points.append(point)
            point = Point(pp[1][0], pp[1][1])
            points.append(point)
            continue
        polygon = Polygon([i for i in points])
        
        if circles is not None:
            circlesTest = np.uint16(np.around(circles))
            index = 0
            for i in circlesTest[0, :]:
                center = Point(i[0], i[1])
                radius = i[2]
                point = geometry.Point(center.x, center.y)
                contains = polygon.contains(point)
                if contains == False:
                    circle = circles[0][index]
                    circle[2]=0
                index = index+1
        
        return