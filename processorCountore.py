import copy
import cv2
import numpy as np
import math
from classifier import classifier
from cornerFig import CircuitSvg
from drawUtils import cvDraw
import drawsvg as drawSvg
from shapely import Point
from shapely.geometry import Polygon
import pathlib
import os
from commonData import LineStatus, ParallStatus, Corner

class processorCountoure:
    def extractContours(finalCountours, circles):
        result = []
        mainCountur = None
        for index in range(len(finalCountours) - 1):
            countour = finalCountours[index]
            countour[4] = processorCountoure.doContours(countour[4])
            if index == 0:
                countour[0] = 1
                mainCountur = countour
                result.append(countour)
                continue
            ok = False
            for counterForTest in result:
                if processorCountoure.compareContours(countour, counterForTest, circles) == True:
                    ok = True
            if ok == False:
                if countour[1] > 1000000:
                    countour[0] = 1
                    mainCountur = countour
                result.append(countour)
        if mainCountur is not None:
            # 0 кордината начальной точки
            # 1 кордината конечной
            # 2 статус
            # 3 длина линии
            # 4 нач индекс
            # 5 расстоячние до следующей точки
            # 6 класс описания угла            
            lines = classifier.classifieCounter( mainCountur[4], 100, 0, -1 )
            # shift = lines[0][4][0]+130
            lastIndex = lines[0][4][1]
            all = len(mainCountur[4])
            shift = all - lastIndex
            # shift = 195
            mainCountur[4] = processorCountoure.shiftContours(mainCountur[4], shift)
            # linesUpdated = classifier.classifieCounter( mainCountur[4], 100, 0, -1 )
            pass
        return result
        # проверка на наличие шума вне контура
        resultUpated = []
        if mainCountur is not None:
            polygonMain = processorCountoure.countureToPolygon(mainCountur[4])
            resultUpated.append(mainCountur)
            for index in range(len(result)):
                if countour[0] == 0:
                    polygon = processorCountoure.countureToPolygon(countour[4])
                    contains = polygonMain.contains(polygon)
                    if contains:
                        resultUpated.append(countour)
        return resultUpated
    def countureToPolygon(countour):
        points=[]
        for pp in countour:
            point = Point(pp[0][0], pp[0][1])
            points.append(point)
            continue
        if len(points)<4:
            return None
        polygon = Polygon([i for i in points])        
        return polygon
    
    def findCornerV0(countour):
        xMin = 100000
        indexMin = -1
        for index in range(len(countour)):
            pp = countour[index]
            if pp[0][0]< xMin:
                xMin = pp[0][0]
                indexMin = index        
        borderX = 10
        yMin = 100000
        indexMinY = -1
        for index in range(len(countour)):
            pp = countour[index]
            if pp[0][0]> xMin -borderX and pp[0][0] < xMin + borderX:
                if pp[0][1]< yMin:
                    yMin = pp[0][1]
                    indexMinY = index        
        return indexMin
    def findCorner(countour):
        yMin = 100000
        indexMin = -1
        for index in range(len(countour)):
            pp = countour[index]
            if pp[0][1]< yMin:
                yMin = pp[0][1]
                indexMin = index        
        # indexMin = 135
        indexMin = 13
        return indexMin
    def shiftContours(countour, indexStart):
        points = []
        for index in range(len(countour)):
            point = countour[index]
            points.append(point)
        s = indexStart
        points = points[-s:] + points[:-s]
        array = np.asarray(points)
        return array
    # выравнивание контура
    def doContours(countour):
        lenCnt = len(countour)
        if lenCnt < 200:
            return countour
        points = []
        for index in range(len(countour)):
            point = countour[index]
            pp = point
            pp[0][0] = pp[0][0]+2
            points.append(pp)
        
        array = np.asarray(points)
        countour = array
        return array
    def compareContours(countourA, countourB, circles):
        areaA = countourA[1]
        areaB = countourB[1]
        delta = abs(areaA - areaB)
        coff = delta / areaA

        M = cv2.moments(countourA[4])
        cAX = int(M["m10"] / M["m00"])
        cAY = int(M["m01"] / M["m00"])
        M = cv2.moments(countourB[4])
        cBX = int(M["m10"] / M["m00"])
        cBY = int(M["m01"] / M["m00"])
        border = 10
        len = math.sqrt(((cAX - cBX) ** 2) + (cAY - cBY) ** 2)

        isCircle = processorCountoure.isContourCircle(cAX, cAY, circles)
        if isCircle == True:
            return True
        if coff > 1:
            return False
        if len > border:
            return False

        return True

    def isContourCircle(x, y, circles):
        if circles is None:
            return False
        circlesDraw = np.uint16(np.around(circles))
        for i in circlesDraw[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            len = math.sqrt(((x - center[0]) ** 2) + ((y - center[1]) ** 2))
            if len < 10:
                return True
        return False

    def calkCenter(countour):
        M = cv2.moments(countour[4])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return cX, cY
