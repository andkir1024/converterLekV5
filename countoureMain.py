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
from commonData import LineStatus, ParallStatus, Corner, TypeСutout,svgCountoure
from sequencer import sequencer


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
    def addChalfCircle(self, pp0, pp1, pp2, pp3, isLeft = False):
        bezP1, bezP2, centroid, bezP3, bezP4, sB = bezier.createHalfCircle(pp0, pp1, pp2, pp3, isLeft)
        
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
        
    def createFlatCouture(self, lines):
        pp0, pp1 = bezier.convertToPoint(lines[0])
        self.addM(pp0)
        for index in range(len(lines)-1):
            line = lines[index]
            lineN = lines[index+1]
            self.createStepCouture(line, lineN)
        self.createStepCouture(lines[len(lines)-1], lines[0])
        self.addZ()
    def createStepCouture(self, line, lineN):
        pp0, pp1 = bezier.convertToPoint(line)
        # self.addM(pp0)
        self.addL(pp1)
        lineType = line[6].cross
        isCorner = geometryUtils.checkCorner(line, lineN)
        isDownU = geometryUtils.checkDownU(line, lineN)

        contours = line[6].pointsFig.copy()
        peri = cv2.arcLength(contours,False)
        # параллельные последовательные линии
        if lineType == ParallStatus.hor:
            # approx = cv2.approxPolyDP(contours, 0.001* peri, False)
            approx = cv2.approxPolyDP(contours, 0.01 * peri, False)
            path = sequencer.checkPath(approx)
            typeСutout, pp0, pp1, pp2 = sequencer.classifyPath(path, approx)
            if typeСutout == TypeСutout.undifined:
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                if maxVal > 0:
                    coff = peri / maxVal
                    if coff < 5:
                        self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max)
                    else:
                        self.cornerBetweenToParallelLinesOneSplne( line, lineN)
            else:
                self.cutoutUType0(pp0, pp1, pp2)
                pass
        elif lineType == ParallStatus.vert and isDownU == False:
            approx = cv2.approxPolyDP(contours, 0.001* peri, False)
            maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
            if maxVal > 0:
                coff = peri / maxVal
                if coff < 5:
                    self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max)
                else:
                    self.cornerBetweenToParallelLinesOneSplne( line, lineN)
            pass
        else:
            if isCorner == True:
                approx = cv2.approxPolyDP(contours, 0.01* peri, False)
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                if maxVal > 0:
                    coff = peri / maxVal
                    if coff < 2:
                        # угол с линией
                        self.cornerRight(line, lineN,pp0Max, pp1Max)
                        pass
                    else:
                        # угол скругленный
                        self.cornerRightSmooth(line, lineN)
                        pass
            if isDownU == True:
                self.cornerUDown(line, lineN)
        return
    def cornerUDown(self, line, lineN):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        # pp1, pp2 = bezier.aligmentHor(pp1, pp2)
        self.addChalfCircle(pp0, pp1, pp2, pp3, True)
        return
    # соединение нижний вырез
    def cornerBetweenToParallelLinesOneSplne(self, line, lineN):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])

        self.cornerBy2Point(pp1, pp2)
        return
    # соединение пареллельных линий (линии внутри нет)
    def cornerBetweenToParallelLinesOneSplne(self, line, lineN):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])

        self.cornerBy2Point(pp1, pp2)
        return
    # углы --------------------------------------------------------------
    # соединение пареллельных линий (есть линия внутри)
    def cornerBetweenToParallelLinesTwoSpline(self, line, lineN, pp0Max, pp1Max):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)

        coff1 = 0.6
        self.cornerBy3Point(pp1, ppIntersected0, pp1Max,coff1)
        self.addL(pp0Max)
        self.cornerBy3Point(pp0Max, ppIntersected1, pp2,coff1)
        
        # self.addL(ppIntersected0)
        # self.addL(pp1Max)
        # self.addL(pp0Max)
        # self.addL(ppIntersected1)
        # self.addL(pp2)
        return
    # угол по 2 точкам (для параллельных прямых)
    def cornerBy2Point(self, pp0, pp1, coff1 = 0.7, coff2 = 0.7):
        pp01 = Point(pp1.x,pp0.y)
        pp10 = Point(pp0.x,pp1.y)
        
        bezP0 = bezier.interpolatePoint(pp01, pp0, coff1)
        bezP1 = bezier.interpolatePoint(pp10, pp1, coff2)
        self.addC(bezP0, bezP1, pp1)
        return
    # угол по 3 точкам
    def cornerBy3Point(self, pp0, pp1, pp2, coff1):
        bezP0 = bezier.interpolatePoint(pp0, pp1, coff1)
        bezP1 = bezier.interpolatePoint(pp2, pp1, coff1)
        self.addC(bezP0, bezP1, pp2)
        return
    # прямой не сглаженный угол
    def cornerRight(self, lineA, lineB,pp0Max, pp1Max):
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)
        
        coff1 = 0.8

        # self.addL(pp0Max)
        # self.addL(pp1Max)
        
        # self.addL(ppIntersected0)
        # self.addL(ppIntersected1)
        
        self.cornerBy3Point(pp1, ppIntersected0, pp1Max,coff1)
        self.addL(pp0Max)
        self.cornerBy3Point(pp0Max, ppIntersected1, pp2,coff1)
       
        return
    # прямой сглаженный угол
    def cornerRightSmooth(self, lineA, lineB):
        coff1 = 0.55
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])
        
        ppIntersected = geometryUtils.calkPointIntersection(pp0, pp1, pp2, pp3)
        self.cornerBy3Point(pp1, ppIntersected, pp2, coff1)
        return
    # вырезы --------------------------------------------------------------
    def cutoutUType0(self, pp0,pp1, pp2):
        self.cornerBy2Point(pp2, pp1, 0.3, 0.3)
        self.cornerBy2Point(pp1, pp0, 0.3, 0.3)
        return
    
    def UneckSvg(self, ppStart, cornSize0, ppLeft, cornSize1, ppDown, cornSize2, ppRight, cornSize3, ppEnd):
        self.addL(ppStart)
        self.addL(ppLeft)
        self.addL(ppDown)
        self.addL(ppRight)
        return