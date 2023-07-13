import enum

import cv2
import numpy as np
from bezier import bezier
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import geometry
from shapely import affinity
from geomUtils import *
from commonData import LineStatus, ParallStatus, Corner, TypeСutout,svgCountoure
from sequencer import sequencer


class svgPath:
    svg = []
    Mpresent = False
    HorLine = None
    def __init__(self):
        self.data = []
        self.svg.clear()
    def addM(self, pp):
        param= (svgCountoure.svgM, pp)
        self.Mpresent = True
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
        # dpi = 1
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
    def testPointInCounture(self, lines, circles, mastInside, doScale):
        circlesNew = []
        points=[]
        for pp in lines:
            point = Point(pp[0][0], pp[0][1])
            points.append(point)
            point = Point(pp[1][0], pp[1][1])
            points.append(point)
            continue
        if len(lines)<4 and mastInside == True:
            return
        polygon = Polygon([i for i in points])
        if doScale:
            polygon = affinity.scale(polygon, xfact=1.2, yfact=1.2)
        
        if circles is not None:
            circlesTest = np.uint16(np.around(circles))
            index = 0
            for i in circlesTest[0, :]:
                center = Point(i[0], i[1])
                radius = i[2]
                point = geometry.Point(center.x, center.y)
                contains = polygon.contains(point)
                if mastInside == False:
                    contains = False if contains else True
                if contains == False:
                    circle = circles[0][index]
                    circle[2]=0
                index = index+1
        
        return
        
    def createFlatCouture(self, lines):
        # pp0, pp1 = bezier.convertToPoint(lines[0])
        # lines.insert(0, lines[5])
        # lines.pop()
        for index in range(len(lines)-1):
            line = lines[index]
            lineN = lines[index+1]
            # if line[1][0] != lineN[0][0]:
            self.createStepCouture(line, lineN, index)
        self.createStepCouture(lines[len(lines)-1], lines[0], -1)
        self.addZ()
    def createStepCouture(self, line, lineN, index):
        pp0, pp1 = bezier.convertToPoint(line)
        # self.addM(pp0)
        # if index == 0:
            # self.addM(pp1)
        lineType = line[6].cross
        isCorner = geometryUtils.checkCorner(line, lineN)
        isDownU = geometryUtils.checkDownU(line, lineN)
        isHorizontal = geometryUtils.checkHorizont(line, lineN)
        # isHorizontal = False

        contours = line[6].pointsFig.copy()
        # return
        # andy
        # if len(contours) <=2:
            # return
        peri = cv2.arcLength(contours,False)
        figSize = sequencer.getSizeFig(line, 50)
        figSizeN = sequencer.getSizeFig(lineN, 50)
        if figSize[2]:
            if figSize[0] <=2 and figSize[1] <=2:
                return
        
        # if figSize[2]:
            # self.cornerRightSmooth(line, lineN)

            # self.cornerBetweenToParallelLinesOneSplne( line, lineN)
            # return
        # параллельные последовательные линии
        # lineType = None
        # if lineType == ParallStatus.hor or isHorizontal:
        if isHorizontal:
            if figSize[2]:
                self.cornerBetweenToParallelLinesOneSplne( line, lineN, index)
                return

            # approx = cv2.approxPolyDP(contours, 0.001* peri, False)
            approx = cv2.approxPolyDP(contours, 0.003 * peri, False)
            path = sequencer.checkPath(approx)
            typeСutout, ppAll = sequencer.classifyPath(path, approx, lineN)
            if typeСutout == TypeСutout.undifined:
                # pass                
                # self.cornerBetweenToParallelLinesOneSplne( line, lineN)
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                # self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max)
                # self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max)
                if maxVal > 0:
                    coff = peri / maxVal
                    if coff < 5:
                        self.cornerBetweenToParallelLinesTwoSpline( line, lineN, pp0Max, pp1Max, index)
                    else:
                        self.cornerBetweenToParallelLinesOneSplne( line, lineN, index)
                return
            elif typeСutout == TypeСutout.UType0:
                self.cutoutUType0(ppAll, index)
                return
            elif typeСutout == TypeСutout.UType1:
                self.cutoutUType1(ppAll, index)
                return
            elif typeСutout == TypeСutout.UType2:
                self.cutoutUType2(ppAll, index)
                return
            elif typeСutout == TypeСutout.UType3:
                self.cutoutUType3(ppAll, index)
                return
        elif lineType == ParallStatus.vert and isDownU == False:
            approx = cv2.approxPolyDP(contours, 0.001* peri, False)
            maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
            if maxVal > 0:
                coff = peri / maxVal
                if coff < 5:
                    self.cornerBetweenToParallelLinesTwoSplineHor( line, lineN, pp0Max, pp1Max, index)
                else:
                    self.cornerBetweenToParallelLinesOneSplne( line, lineN, index)
            return
        else:
            # isCorner = True
            if isCorner == True:
                approx = cv2.approxPolyDP(contours, 0.01* peri, False)
                maxVal, pp0Max, pp1Max = geometryUtils.lenghtContoureLine(approx)
                if maxVal > 0:
                    coff = peri / maxVal
                    if coff < 2:
                        # угол с линией
                        self.cornerRight(line, lineN,pp0Max, pp1Max, index)
                        pass
                    else:
                        # угол скругленный
                        # if index == 5 and index == 4:
                        self.cornerRightSmooth(line, lineN, index)
                    return
                # else:
                    # self.cornerBetweenToParallelLinesOneSplne( line, lineN)
                return
            if isDownU == True:
                self.cornerUDown(line, lineN, index)
                return
        self.cornerRightSmall(line, lineN, index)
        return
    def cornerUDown(self, line, lineN, index):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        # pp1, pp2 = bezier.aligmentHor(pp1, pp2)
        # self.doInitPosition(index, pp0)
        self.addL(pp1)
        self.addChalfCircle(pp0, pp1, pp2, pp3, True)
        return
    # соединение пареллельных линий (линии внутри нет)
    def cornerBetweenToParallelLinesOneSplne(self, line, lineN, index):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        # if self.HorLine is not None:
        #     pp0 = self.HorLine[0][1]
        #     pp1 = self.HorLine[0][2]

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])

        self.doInitPosition(index, pp1)
        self.cornerBy2Point(pp1, pp2)
        return
    # углы --------------------------------------------------------------
    # соединение пареллельных линий (есть линия внутри)
    def cornerBetweenToParallelLinesTwoSplineHor(self, line, lineN, pp0Max, pp1Max, index):
        # if index != 1:
            # return
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        
        # pp1Max = Point(pp1Max.x- 20,pp1Max.y)
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)
        coff1 = 0.6
        self.doInitPosition(index, pp1)
        self.cornerBy3Point(pp1, ppIntersected0, pp1Max,coff1)
        self.addL(pp0Max)
        self.cornerBy3Point(pp0Max, ppIntersected1, pp2,coff1)
        
        # self.addL(ppIntersected0)
        # self.addL(pp1Max)
        # self.addL(pp0Max)
        # self.addL(ppIntersected1)
        # self.addL(pp2)
        return
    # соединение пареллельных линий (есть линия внутри)
    def cornerBetweenToParallelLinesTwoSpline(self, line, lineN, pp0Max, pp1Max, index):
        pp0 = Point(line[0][0],line[0][1])
        pp1 = Point(line[1][0],line[1][1])

        pp2 = Point(lineN[0][0],lineN[0][1])
        pp3 = Point(lineN[1][0],lineN[1][1])
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)
        coff1 = 0.6

        self.doInitPosition(index, pp1)
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
        # pp01 = Point(pp1.x,pp0.y)
        # pp10 = Point(pp0.x,pp1.y)
        
        # bezP0 = bezier.interpolatePoint(pp01, pp0, coff1)
        # bezP1 = bezier.interpolatePoint(pp10, pp1, coff2)
        # self.addC(bezP0, bezP1, pp1)
        # return
        
        ab = LineString([pp0, pp1])
        centroid = ab.centroid

        pp01 = Point(centroid.x,pp0.y)

        pp10 = Point(centroid.x,pp1.y)

        self.cornerBy3PointAngled(pp0, pp01, centroid, 0.3, True)
        self.cornerBy3PointAngled(centroid, pp10, pp1, 0.3, False)
        
        return
    # угол по 3 точкам
    def cornerBy3PointAngled(self, pp0, pp1, pp2, coff1, dir):
        if pp0 is None or pp1 is None or pp2 is None:
            return
        if dir:
            bezP0 = bezier.interpolatePoint(pp0, pp1, coff1)
            # bezP1 = bezier.interpolatePoint(pp2, pp1, coff1)
            # ab = LineString([bezP0, pp1])
            bezP1 = bezier.interpolatePoint(bezP0, pp2, coff1)
            self.addC(bezP0, bezP1, pp2)
        else:
            bezP0 = bezier.interpolatePoint(pp2, pp1, coff1)
            bezP1 = bezier.interpolatePoint(bezP0, pp0, coff1)
            self.addC(bezP1, bezP0, pp2)
        return
    # угол по 3 точкам
    def cornerBy3Point(self, pp0, pp1, pp2, coff1):
        if pp0 is None or pp1 is None or pp2 is None:
            return
        bezP0 = bezier.interpolatePoint(pp0, pp1, coff1)
        bezP1 = bezier.interpolatePoint(pp2, pp1, coff1)
        self.addC(bezP0, bezP1, pp2)
        return
    # прямой не сглаженный угол
    def cornerRight(self, lineA, lineB,pp0Max, pp1Max, index):
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])
        
        ppIntersected0 = geometryUtils.calkPointIntersection(pp0, pp1, pp0Max, pp1Max)
        ppIntersected1 = geometryUtils.calkPointIntersection(pp2, pp3, pp0Max, pp1Max)
        if ppIntersected0 is None:
            return
        if ppIntersected1 is None:
            return
        ppIntersected0 = ppIntersected0.coords[0]
        ppIntersected1 = ppIntersected1.coords[0]
        coff1 = 0.8

        # self.addL(pp0Max)
        # self.addL(pp1Max)
        
        # self.addL(ppIntersected0)
        # self.addL(ppIntersected1)
        
        # if index == 0: 
        #     self.addM(pp1)
        # else:
        #     self.addL(pp1)
        self.doInitPosition(index, pp1)
        self.cornerBy3Point(pp1, ppIntersected0, pp1Max,coff1)
        self.addL(pp0Max)
        self.cornerBy3Point(pp0Max, ppIntersected1, pp2,coff1)
       
        return
    # очень мальнький сглаженный угол
    def cornerRightSmall(self, lineA, lineB, index):
        coff1 = 0.55
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])

        pp1 = bezier.interpolatePointByPixel(pp0, pp1, 10)
        pp2 = bezier.interpolatePointByPixel(pp3, pp2, 10)
        
        
        ppIntersected = geometryUtils.calkPointIntersection(pp0, pp1, pp2, pp3)
        # if ppIntersected is not None:
        # if index == 0: 
        #     self.addM(pp1)
        # else:
        #     self.addL(pp1)
        self.doInitPosition(index, pp1)
        self.cornerBy3Point(pp1, ppIntersected, pp2, coff1)
        # self.addL(pp2)
        return
    # прямой сглаженный угол
    def cornerRightSmooth(self, lineA, lineB, index):
        self.cornerRightSmoothNew(lineA, lineB, index)
        # self.cornerRightSmoothOld(lineA, lineB, index)

    def cornerRightSmoothNew(self, lineA, lineB, index):
        cornerFig= lineA[6]
        coff1 = 0.65
        
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])

        # if index == 4:
        
        if index == -1:
            index = -1
        
        if index == 1:
            if pp0.x > pp1.x and pp0.y < 2000:
                pp0, pp1 = pp1, pp0
        dir = geometryUtils.directionCurveIntersectionV2(pp0, pp1, pp2, pp3, index)

        # if index == 5 or index == 4:
        if dir:
            ppCoff, ip0, ip1, bezir0, bezir1 = geometryUtils.calkLineCurveIntersectionV2(cornerFig, pp0, pp1, pp2, pp3)
            if bezir0 is None:
                ppCoff, ip0, ip1, bezir0, bezir1 = geometryUtils.calkLineCurveIntersection(cornerFig, pp0, pp1, pp2, pp3)
        else:
            ppCoff, ip0, ip1, bezir0, bezir1 = geometryUtils.calkLineCurveIntersection(cornerFig, pp0, pp1, pp2, pp3)
        if ppCoff is None:
            return
        self.doInitPosition(index, pp1)
        
        # self.cornerBy3Point(pp1, bezir0, ip0, 0.1)
        # self.addL(ppCoff)
        # self.cornerBy3Point(ppCoff, bezir1, ip1, 0.1)
        
        self.addC(bezir0, ip0, ppCoff)
        self.addC(ip1, bezir1, pp2)
        
        # index =-1
        # # index = 0
        # if index == 0:
        #     self.addC(bezir0, ip0, ppCoff)
        #     self.addC(ip1, bezir1, pp2)
        # else:
        #     self.cornerRightSmoothOld(lineA, lineB, index)
        
        # self.addL(bezir0)
        # self.addL(ip0)
        # self.addL(ppCoff)
        # self.addL(ip1)
        # self.addL(bezir1)
        # self.addL(pp2)
        
        return
    def cornerRightSmoothOld(self, lineA, lineB, index):
        cornerFig= lineA[6]
        coff1 = 0.55
        coff1 = 0.45
        # ok for all
        coff1 = 0.5

        coff1 = 0.65
        
        pp0 = Point(lineA[0][0],lineA[0][1])
        pp1 = Point(lineA[1][0],lineA[1][1])

        pp2 = Point(lineB[0][0],lineB[0][1])
        pp3 = Point(lineB[1][0],lineB[1][1])
        
        ppIntersected = geometryUtils.calkPointIntersection(pp0, pp1, pp2, pp3)
        
        if ppIntersected is not None:
            self.doInitPosition(index, pp1)
            self.cornerBy3Point(pp1, ppIntersected, pp2, coff1)
        return
    # вырезы --------------------------------------------------------------
    def cutoutUType0(self, ppAll, index):
        pp0 = ppAll[0]
        pp1 = ppAll[1]
        pp2 = ppAll[2]
        # if index == 0: 
        #     self.addM(pp2)
        # else:
        #     self.addL(pp2)
        self.doInitPosition(index, pp2)
        self.cornerBy2Point(pp2, pp1, 0.3, 0.3)
        self.cornerBy2Point(pp1, pp0, 0.3, 0.3)
        return
    def cutoutUType1(self, ppAll, index):
        pp0 = ppAll[0]
        pp1 = ppAll[1]
        pp2 = ppAll[2]
        ppX0 = ppAll[3]
        ppX1 = ppAll[4]
        dx = (ppX1 - ppX0)/2
        # leftt
        ppL0 = Point(ppX0, pp2.y + dx/4)
        ppL1 = Point(ppX0, pp1.y - dx)

        ppI0 = Point(ppX0, pp2.y)
        ppI1 = Point(ppX0, pp1.y)
        
        coff1 = 0.6
        self.doInitPosition(index, pp2)
        self.cornerBy3Point(pp2, ppI0, ppL0,coff1)
        self.addL(ppL1)
        self.cornerBy3Point(ppL1, ppI1, pp1,coff1)
        # right
        ppR0 = Point(ppX1, pp0.y + dx/4)
        ppR1 = Point(ppX1, pp1.y - dx)

        ppI0 = Point(ppX1, pp1.y)
        ppI1 = Point(ppX1, pp0.y)

        # self.addL(ppI0)
        # self.addL(ppR1)
        # self.addL(ppR0)
        # self.addL(ppI1)
        
        self.cornerBy3Point(pp1, ppI0, ppR1, coff1)
        self.addL(ppR0)
        self.cornerBy3Point(ppR0, ppI1, pp0, coff1)

        # self.cornerBy2Point(pp2, pp1, 0.1, 0.1)
        # self.cornerBy2Point(pp1, pp0, 0.1, 0.1)
        return
    
    def cutoutUType2(self, ppAll, index):
        pp0 = ppAll[0]
        pp1 = ppAll[1]
        pp2 = ppAll[2]
        ppX0 = ppAll[3]
        ppX1 = ppAll[4]
        ppX2 = ppAll[5]
        
        pp1 = Point(ppX0 + (ppX1 - ppX0)/2, pp1.y)
        pp2 = Point(ppX1, pp0.y)
        
        dx = (ppX1 - ppX0)/2
        # leftt
        ppL0 = Point(ppX0, pp2.y + dx/4)
        ppL1 = Point(ppX0, pp1.y - dx)

        ppI0 = Point(ppX0, pp2.y)
        ppI1 = Point(ppX0, pp1.y)
        
        coff1 = 0.6
        self.doInitPosition(index, pp2)
        self.cornerBy3Point(pp2, ppI0, ppL0,coff1)
        self.addL(ppL1)
        self.cornerBy3Point(ppL1, ppI1, pp1,coff1)
        # right
        ppR0 = Point(ppX1, pp0.y + dx/4)
        ppR1 = Point(ppX1, pp1.y - dx)

        ppI0 = Point(ppX1, pp1.y)
        ppI1 = Point(ppX1, pp0.y)
        
        self.cornerBy3Point(pp1, ppI0, ppR1, coff1)
        self.addL(ppR0)
        self.cornerBy3Point(ppR0, ppI1, pp0, coff1)

        return

    def findNexSpline(self, ppAll, indexStart):
        for index in range(indexStart, len(ppAll[0])):
            spline = ppAll[0][index]
            dir = spline[1]
            if dir == 1:
                return spline
        return None

    def getCenterLines(self, lineA, lineB):
        dx = abs(lineA[1].x-lineB[1].x)/2
        x = min(lineA[1].x, lineB[1].x) + dx
        return x
    def doInitPosition(self, index, pp):
        if index == 0: 
            self.addM(pp)
        else:
            # self.addL(pp)
            if self.Mpresent == False:
                self.addM(pp)
            else:
                self.addL(pp)

    def cutoutUType3(self, ppAll, indexLine):
        ppE = ppAll[1]
        ppS = ppAll[2]
        all = len(ppAll[0])
        for index in range(all - 1):
            if index == 0:
                self.HorLine = None

            spline = ppAll[0][index]
            line = spline[0]

            splineN = ppAll[0][index+1]
            lineN = splineN[0]

            dir = spline[1]
            dirN = splineN[1]
            if dir == 0 and dirN == 1:
                pp0 = ppS
                pp1 = splineN[2]
                xx= self.getCenterLines(line, lineN)
                pp1 = Point(xx, pp1.y)
                ppL0 = line[1]
                ppL1 = line[2]
                ppNL0 = lineN[1]
                ppNL1 = lineN[2]
                ppL0, ppNL1 = bezier.aligmentHor(ppL0, ppNL1)
                ppL1, ppNL0 = bezier.aligmentHor(ppL1, ppNL0)
                # left

                ppI0 = Point(ppL0.x, pp0.y)
                ppI1 = Point(ppL1.x, pp1.y)

                coff1 = 0.6
                if index == 0:
                    self.doInitPosition(indexLine, ppS)
                else:
                    self.addL(ppS)
                # self.addM(Point(0,0))

                self.cornerBy3Point(ppS, ppI0, ppL1,coff1)
                self.addL(ppL0)
                self.cornerBy3Point(ppL0, ppI1, pp1,coff1)

                # right
                ppNL0 = lineN[1]
                ppNL1 = lineN[2]
                ppNI0 = Point(ppNL0.x, pp0.y)
                ppNI1 = Point(ppNL1.x, pp1.y)
                self.cornerBy3Point(pp1, ppNI1, ppNL1,coff1)
                self.addL(ppNL0)
                # проверка есть ли далее горизонтальная линия или конец
                if index < all - 2:
                    splineNN = ppAll[0][index+2]
                    lineNN = splineNN[0]
                    dirNN = splineNN[1]
                    if dirNN == -1:
                        pp2 = lineNN[2]
                        self.cornerBy3Point(ppNL0, ppNI0, pp2,coff1)
                        ppS = lineNN[1]    
                        # добавлено для продлжения и выравнивания горизонтальных линий
                        if abs(ppS.y - ppE.y) > 5 and index > all - 3:
                            self.addL(ppS)
                            self.cornerBy2Point(ppS, ppE)
                            
                            
                        # self.addL(ppS)
                        # self.HorLine = splineNN
                        continue
                else:
                    pp2 = ppE
                    self.cornerBy3Point(ppNL0, ppNI0, pp2,coff1)
                    
                continue
            if dir == 1 and dirN == -10:
                pp0 = ppS
                pp1 = splineN[2]
                xx= self.getCenterLines(line, lineN)
                pp1 = Point(xx, pp1.y)
                ppL0 = line[1]
                ppL1 = line[2]
                ppNL0 = lineN[1]
                ppNL1 = lineN[2]
                ppL0, ppNL1 = bezier.aligmentHor(ppL0, ppNL1)
                ppL1, ppNL0 = bezier.aligmentHor(ppL1, ppNL0)
                # left

                ppI0 = Point(ppL0.x, pp0.y)
                ppI1 = Point(ppL1.x, pp1.y)

                coff1 = 0.6

                self.cornerBy3Point(ppS, ppI0, ppL1,coff1)
                self.addL(ppL0)
                self.cornerBy3Point(ppL0, ppI1, pp1,coff1)

                # right
                ppNL0 = lineN[1]
                ppNL1 = lineN[2]
                ppNI0 = Point(ppNL0.x, pp0.y)
                ppNI1 = Point(ppNL1.x, pp1.y)
                self.cornerBy3Point(pp1, ppNI1, ppNL1,coff1)
                self.addL(ppNL0)
                continue
            if dir == -1 and dirN == 0 and index >= all - 2:
                self.addL(line[1])
                pp0 = line[2]
                pp1 = ppE
                ppL0 = lineN[1]
                ppL1 = lineN[2]

                ppI0 = Point(ppL0.x, pp0.y)
                ppI1 = Point(ppL1.x, pp1.y)

                coff1 = 0.6
                self.doInitPosition(indexLine, ppS)
                self.cornerBy3Point(ppS, ppI0, ppL1,coff1)
                self.addL(ppL0)
                self.cornerBy3Point(ppL0, ppI1, pp1,coff1)
                continue
            if dir == -1:
                # self.addL(line[2])
                self.addL(line[1])
                continue
        return
