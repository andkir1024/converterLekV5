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
        self.svg.clear()
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
    def centerLine(self, line):
        pointS = Point(line[0][0], line[0][1])
        pointE = Point(line[1][0], line[1][1])
        xCenter = pointS.x + ((pointS.x - pointE.x)/2)
        yCenter = pointS.y + ((pointS.y - pointE.y)/2)
        return Point(xCenter, yCenter)
        
    def createFlatCouture(self, lines):
        for index in range(len(lines)):
            line = lines[index]
            if index == 1:
                lineP = lines[index-1]
                lineN = lines[index+1]

                pointS = Point(lineP[1][0], lineP[1][1])
                ppStart = geometry.Point(pointS.x, pointS.y)

                pointE = Point(lineN[0][0], lineN[0][1])
                ppEnd = geometry.Point(pointE.x, pointE.y)
                
                ppDown = self.centerLine(line)
                
                self.UneckSvg(ppStart, 40, 60, ppDown, 60,40, ppEnd)
                continue
            pp0, pp1 = bezier.convertToPoint(line)
            if index == 0:
                self.addM(pp0)
            else:
                self.addL(pp0)
            self.addL(pp1)
        self.addZ()
    def UneckSvg(self, ppStart, cornSize0, cornSize1, ppDown, cornSize2,cornSize3, ppEnd):
        return