import enum
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from cornerFig import LineStatus, ParallStatus, CircuitSvg, Corner
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
# from scipy import interpolate

class classifier:
    # вырезаем короткие линии
    def packLine( last_point, curr_point, border, index):
        x1=int(last_point[0])
        y1=int(last_point[1])
        x2=int(curr_point[0])
        y2=int(curr_point[1])
        lenLine = int(math.sqrt( ((x1-x2)**2)+((y1-y2)**2)))
        if lenLine > border:
            # 0 кордината начальной точки
            # 1 кордината конечной
            # 2 статус
            # 3 длина линии
            # 4 
            # 5 расстоячние до следующей точки
            # 6 класс описания угла
            return  [(x1, y1), (x2, y2), LineStatus.undefined, lenLine, index, 0, None]
        return None
    # выделение линий длиной не менее border из точек контура
    def extractLinesFromCircuit(sel_countour, border, startPoint, finPoint, closed):
        lines = []
        peri = cv2.arcLength(sel_countour,True)
        # sel_countour = cv2.approxPolyDP(sel_countour, 0.0001 * peri, True)
        all_points = len(sel_countour)
        if finPoint < 0:
            finPoint = all_points

        # a = 2 % len(sel_countour)
        # sel_countour1 = sel_countour[-a:] + sel_countour[:-a]
        # sel_countour = np.delete(sel_countour, 0)
        # sel_countour.remove(0)
        # del sel_countour[0]
        
        indexPrev=-1
        # border =10
        startP = None
        for index in range(startPoint+1, finPoint):
            curr_point=sel_countour[index][0]
            last_point = sel_countour[index-1][0]

            line =classifier.packLine(last_point,curr_point, border, (indexPrev,index))
            if line is not None:
                lines.append(line)
                indexPrev = index
                if startP is  None:
                    startP = startPoint
        if closed == True:
            # line =classifier.packLine(last_point,sel_countour[startP][0], border, (indexPrev,finPoint))
            line =classifier.packLine(last_point,sel_countour[startPoint][0], border, (indexPrev,finPoint))
            # line =classifier.packLine(last_point,sel_countour[startPoint][0], 10, (indexPrev,finPoint))
            if line is not None:
                lines.append(line)
        lines = lines[::-1]
        return lines
    # 1 начало работы класификатора
    def classifieCounter(sel_countour, border, startPoint, finPoint):
        lines =classifier.extractLinesFromCircuit(sel_countour, border, startPoint, finPoint, True)
        if len(lines) == 0:
            return None
        lines =classifier.AligmentLinesInConture(lines)
        classifier.doPropertyesFig(sel_countour, lines)
        return lines
    # выравнивание линий по начало конец
    def AligmentLinesInConture(lines):
        linesDst = []
        linesDst.append(lines[0].copy())
        linesDst[-1] = classifier.swapPoint(linesDst[-1])
        for index in range(1, len(lines)-0):
            # последняя точка текущей линии
            linesDst.append(lines[index].copy())

            pointAF = linesDst[-2][1]
            # start
            pointBS = linesDst[-1][0]
            # finish
            pointBF = linesDst[-1][1]

            distAFBS = CircuitSvg.distancePoint(pointAF, pointBS) 
            distAFBF = CircuitSvg.distancePoint(pointAF, pointBF)
            if distAFBS > distAFBF:
                linesDst[-1] = classifier.swapPoint(linesDst[-1])
                linesDst[-1][5] = int(distAFBF)
            else:
                linesDst[-1][5] = int(distAFBS)
                
            continue
        return linesDst
    # 2 расчет параметров  класификатора
    def doPropertyesFig(sel_countour, lines):
        allLines = len(lines)
        for index in range(0, allLines):
            line = lines[index]
            lineNext = lines[0]
            if index < allLines-1:
                lineNext = lines[index+1]
            minX,minY,maxX,maxY,linesFig = classifier.calkFigRect(sel_countour, lines, line, lineNext)
            # определение точки пересечения для закругдегия угла
            cross = classifier.calkCrossLine(line, lineNext, minX,minY,maxX,maxY,linesFig )
            points = classifier.calkFigPoints(sel_countour, lines, line, lineNext)
            corner = Corner(minX,minY,maxX,maxY,linesFig,cross, points)
            line[6] = corner
        return
    # определение того как соеденить сегменты
    def testSegment(countour, prevLine, nextLine, cente ):
        return
    def drawFigRect(img, sel_countour, lines):
        thickness = 10
        allLines = len(lines)
        for index in range(0, allLines):
            line = lines[index]
            corner = line[6]
            img = cv2.rectangle(img, (corner.minX,corner.minY), (corner.maxX, corner.maxY), (0, 255, 0), thickness)
            msg = f"{line[4][0]},{line[4][1]},{index}"
            cv2.putText(img, msg, (corner.minX, corner.minY), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,0,0),4)
            cv2.line(img, line[0], line[1], color=(0,0,255), thickness=thickness)
            if ParallStatus.isCoord(corner.cross) == True:
                cv2.circle(img, corner.cross, radius=0, color=(255, 0, 0), thickness=50)
            # if corner.cross != None:
                # cv2.circle(img, corner.cross, radius=0, color=(255, 0, 0), thickness=50)
            if corner.linesFig is not None:
                for lineFig in corner.linesFig: 
                    cv2.line(img, lineFig[0], lineFig[1], color=(255,0,0), thickness=thickness)
        return
    def calkFigRect(sel_countour, lines, line,lineNext):
        indexStart, indexFinish = line[4]
        if indexFinish < 0:
            return None,None,None,None,None
        if indexStart < 0:
            indexStart = 0
        maxX = maxY = -100000
        minX = minY = 100000
        for index in range(indexStart, indexFinish):
            point = sel_countour[index]
            maxX = max(maxX, point[0][0])
            minX = min(minX, point[0][0])

            maxY = max(maxY, point[0][1])
            minY = min(minY, point[0][1])
        linesFig =classifier.extractLinesFromCircuit(sel_countour, 20, indexStart+1, indexFinish-1, False)
        if len(linesFig) == 0:
            linesFig = None
        return (minX,minY,maxX,maxY,linesFig)
    def calkFigPoints(sel_countour, lines, line,lineNext):
       
        indexStart, indexFinish = line[4]
        if indexFinish < 0:
            return None
        if indexStart < 0:
            indexStart = 0
        points = []
        for index in range(indexStart, indexFinish):
            point = sel_countour[index]
            points.append(point[0])
        if len(points) == 0:
            return None
        # contours = [np.array([[1,1],[10,50],[50,50]], dtype=np.int32) , np.array([[99,99],[99,60],[60,99]], dtype=np.int32)]
        # drawing = np.zeros([100, 100],np.uint8)
        # points = np.array([[25,25], [70,10], [150,50], [250,250], [100,350]])
        # a = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]])
        array = np.asarray(points)
        return array
        
        # return points
    def calkCrossLine(line, lineNext, minX,minY,maxX,maxY,linesFig ):
        test = classifier.is_parallel(line, lineNext, minX,minY,maxX,maxY,linesFig )
        if test != ParallStatus.none:
            return test
        LineLong = classifier.lengthenLine(line)
        lineNextLong = classifier.lengthenLine(lineNext)
        # test = LineLong.intersects(lineNextLong)
        result = LineLong.intersection(lineNextLong)
        coords = result.coords
        size = len(coords)
        if size == 0:
            return ParallStatus.none
        return ( int(coords[0][0]), int(coords[0][1]))
    def lengthenLine(line):
        factor = 30
        t0=0.5*(1.0-factor)
        t1=0.5*(1.0+factor)
        firstPoint = line[0]
        secondPoint= line[1]

        x1 = firstPoint[0] +(secondPoint[0] - firstPoint[0]) * t0
        y1 = firstPoint[1] +(secondPoint[1] - firstPoint[1]) * t0

        x2 = firstPoint[0] +(secondPoint[0] - firstPoint[0]) * t1
        y2 = firstPoint[1] +(secondPoint[1] - firstPoint[1]) * t1

        pA = Point(x1,y1)
        pB = Point(x2,y2)
        ab = LineString([pA, pB])
        return ab
    def is_eql(a_delta, b_delta, dist):
        dist = 4
        if b_delta < dist and a_delta < dist:
            return True
        
        # if b_delta > a_delta - dist and b_delta < a_delta + dist:
        #     return True
        return False
    def is_parallel(line1, line2,minX,minY,maxX,maxY,linesFig ):
        a_delta_x = abs(line1[1][0] - line1[0][0])
        a_delta_y = abs(line1[1][1] - line1[0][1])
        b_delta_x = abs(line2[1][0] - line2[0][0])
        b_delta_y = abs(line2[1][1] - line2[0][1])
        
        # паралельность по вертикали
        eqVert = classifier.is_eql(a_delta_x, b_delta_x, 4)
        # паралельность по горизонтали
        eqHor = classifier.is_eql(a_delta_y, b_delta_y, 4)
        if eqHor == True:
            deltaX = line2[0][0] - line1[1][0]
            # начало второй правее конца первой (по горизонтали)
            # if line2[0][0] > line1[1][0]:
            #     # высота второй ниже высоты первой (по верикали)
            #     if line2[0][1] > line1[1][1]:
            #         return ParallStatus.hor_down
            #     else:
            #         return ParallStatus.hor_up
            return ParallStatus.hor

        if eqVert == True:
            return ParallStatus.vert
            # начало второй правее конца первой (по горизонтали)
            # if line2[0][0] > line1[1][0]:
            #     # высота второй ниже высоты первой (по верикали)
            #     if line2[0][1] > line1[1][1]:
            #         return ParallStatus.hor_down
            #     else:
            #         return ParallStatus.hor_up
            # return ParallStatus.hor

        return ParallStatus.none
            
        if eqVert == True and eqHor == True:
            return True 
        else:
            return False 
    def swapPoint(pointSrc):
        pointDst = pointSrc
        pointDst[0],pointDst[1]=pointDst[1],pointDst[0]
        return pointDst
