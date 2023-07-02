import enum

import cv2
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry
from geomUtils import *
from commonData import LineStatus, ParallStatus, Corner,svgCountoure


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
    def addChalfCircle(self, pp0, pp1, pp2, pp3):
        bezP1, bezP2, centroid, bezP3, bezP4, sB = bezier.createHalfCircle(pp0, pp1, pp2, pp3)
        
        param= (svgCountoure.svgCHalfCircle, bezP1, bezP2, centroid, bezP3, bezP4, sB)
        self.svg.append(param)
        return        
    def addC(self, pp0, pp1, pp2):
        param= (svgCountoure.svgC, pp0, pp1, pp2)
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
            if item[0] == svgCountoure.svgCHalfCircle:
                path.C(item[1].x / dpi, item[1].y / dpi, item[2].x / dpi, item[2].y / dpi, item[3].x / dpi, item[3].y / dpi)
                path.C(item[4].x / dpi, item[4].y / dpi, item[5].x / dpi, item[5].y / dpi, item[6].x / dpi, item[6].y / dpi)
            if item[0] == svgCountoure.svgC:
                path.C(item[1].x / dpi, item[1].y / dpi, item[2].x / dpi, item[2].y / dpi, item[3].x / dpi, item[3].y / dpi)
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
        
    def createFlatCoutureV1(self, lines):
        for index in range(len(lines)):
            line = lines[index]
            lineType = line[6].cross
            # debug
            # if index == 1:
            if lineType == ParallStatus.hor:
                lineP = lines[index-1]
                lineN = lines[index+1]
                
                contours = line[6].pointsFig.copy()
                peri = cv2.arcLength(contours,False)
                approx = cv2.approxPolyDP(contours, 0.001* peri, False)
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                if maxVal > 0:
                    coff = peri / maxVal
                    self.cornerBetweenToLines( Point(lineP[0][0],lineP[0][1]), Point(lineP[1][0],lineP[1][1]), pp0Max, pp1Max)
                
                # def calkPointIntersection(lineP, lineB)
                # pp0 = geometryUtils.calkPointIntersection(Point(lineP[0][0], lineP[0][1]), 
                #                                           Point(lineP[1][0], lineP[1][1]),
                #                                           Point(line[0][0], lineP[0][1]),
                #                                           Point(line[0][0], line[0][1]))

                pointS = Point(lineP[1][0], lineP[1][1])
                ppStart = geometry.Point(pointS.x, pointS.y)

                
                ppLeft = geometryUtils.centerConnectionLines(lineP, line)
                ppRight = geometryUtils.centerConnectionLines(line, lineN)

                pointE = Point(lineN[0][0], lineN[0][1])
                ppEnd = geometry.Point(pointE.x, pointE.y)
                
                ppDown = geometryUtils.centerLine(line)
                
                # self.UneckSvg(pp0, 40, ppLeft, 60, ppDown, 60, ppRight, 40, ppEnd)
                # self.UneckSvg(ppStart, 40, ppLeft, 60, ppDown, 60, ppRight, 40, ppEnd)
                # continue
            pp0, pp1 = bezier.convertToPoint(line)
            if index == 0:
                self.addM(pp0)
            else:
                self.addL(pp0)
            self.addL(pp1)
        self.addZ()

    def createFlatCouture(self, lines):
        for index in range(len(lines)):
            line = lines[index]
            pp0, pp1 = bezier.convertToPoint(line)
            self.addM(pp0)
            self.addL(pp1)
            lineType = line[6].cross
            
            if lineType == ParallStatus.hor:
                lineN = lines[index+1]
                contours = line[6].pointsFig.copy()
                peri = cv2.arcLength(contours,False)
                approx = cv2.approxPolyDP(contours, 0.001* peri, False)
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                if maxVal > 0:
                    coff = peri / maxVal
                    if coff < 5:
                        self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max)
                    else:
                        self.cornerBetweenToParallelLinesOneSplne( line, lineN)
        self.addZ()
    # соединение пареллельных линий (линии внутри нет)
    def cornerBetweenToParallelLinesOneSplne(self, line, lineN):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])

        self.cornerBy2Point(pp1, pp2)
        return
    # соединение пареллельных линий (есть линия внутри)
    def cornerBetweenToParallelLinesTwoSpline(self, line, lineN, pp0Max, pp1Max):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)

        self.cornerBy3Point(pp1, ppIntersected0, pp1Max)
        self.addL(pp0Max)
        self.cornerBy3Point(pp0Max, ppIntersected1, pp2)
        
        # self.addL(ppIntersected0)
        # self.addL(pp1Max)
        # self.addL(pp0Max)
        # self.addL(ppIntersected1)
        # self.addL(pp2)
        return
    # угол по 2 точкам (для параллельных прямых)
    def cornerBy2Point(self, pp0, pp1):
        coff1 = 0.7
        pp01 = Point(pp1.x,pp0.y)
        pp10 = Point(pp0.x,pp1.y)
        
        bezP0 = bezier.interpolatePoint(pp01, pp0, coff1)
        bezP1 = bezier.interpolatePoint(pp10, pp1, coff1)
        self.addC(bezP0, bezP1, pp1)
        return
    # угол по 3 точкам
    def cornerBy3Point(self, pp0, pp1, pp2):
        coff1 = 0.6
        bezP0 = bezier.interpolatePoint(pp0, pp1, coff1)
        bezP1 = bezier.interpolatePoint(pp2, pp1, coff1)
        self.addC(bezP0, bezP1, pp2)
        return
    
    def cornerBetweenToLines(self, pp0S, pp0E, pp1S, pp1E):
        ppIntersected = geometryUtils.calkPointIntersection(pp0S, pp0E, pp1S, pp1E)
        if ppIntersected is not None:
            self.addL(ppIntersected)

        # geometryUtils.cornerBetweenToLines(pp0S, pp0E, pp1S, pp1E)
        return
    def UneckSvg(self, ppStart, cornSize0, ppLeft, cornSize1, ppDown, cornSize2, ppRight, cornSize3, ppEnd):
        self.addL(ppStart)
        self.addL(ppLeft)
        self.addL(ppDown)
        self.addL(ppRight)
        return