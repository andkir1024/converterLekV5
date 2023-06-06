import cv2
import numpy as np
import math
import drawsvg as drawSvg
import enum
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from classifier import *
# from shapely.centerline import Centerlinefrom 



class cvDraw:
    def createGray(imgOk, param0):
        imgGray = cv2.cvtColor(imgOk,cv2.COLOR_BGR2GRAY)

        imgGray  = cv2.medianBlur(imgGray,7)

        # 1 повышение резкости
        kernel = np.array([[-1,-1,-1], 
                       [-1, 39,-1],
                       [-1,-1,-1]])
        # kernel = 1/3 * kernel
        # imgGray = cv2.filter2D(imgGray, -1, kernel) 

        # 2 выделение границ
        cThr=[100,100]
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgBlur = cv2.Canny(imgBlur,cThr[0],cThr[1])
        # imgGray = cv2.bitwise_not(imgBlury)
        
        kernel = np.ones((3,3))
        # imgGray = cv2.dilate(imgGray,kernel,iterations=13)
        # imgGray = cv2.erode(imgGray,kernel,iterations=1)
        
        # img_grey  = cv2.medianBlur(img_grey,1)
        # img_grey = cv2.blur(img_grey, (3, 3))
        # return imgBlur
        return imgGray
        # return imgCanny
        
    def testLine( img, last_point, curr_point, border = 100):
        x1=int(last_point[0])
        y1=int(last_point[1])
        x2=int(curr_point[0])
        y2=int(curr_point[1])
        lenLine = math.sqrt( ((x1-x2)**2)+((y1-y2)**2))
        if lenLine > border:
            cv2.line(img, (x1, y1), (x2, y2), (255,0,0), thickness=2)
        return
    
    
    def calkSize( countour ):
        if countour is None:
            return None
        minX = 100000
        maxX = 0
        minY = minX
        maxY = maxX
        for point in countour:
            x =point[0][0]
            y =point[0][1]
            minX = min(minX, x)
            maxX = max(maxX, x)

            minY = min(minY, y)
            maxY = max(maxY, y)
        return [(minX, minY),(maxX, maxY)]
    
    def make_bezier(xys):
        # xys should be a sequence of 2-tuples (Bezier control points)
        n = len(xys)
        combinations = cvDraw.pascal_row(n-1)
        def bezier(ts):
            # This uses the generalized formula for bezier curves
            # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
            result = []
            for t in ts:
                tpowers = (t**i for i in range(n))
                upowers = reversed([(1-t)**i for i in range(n)])
                coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
                result.append(
                    tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
            return result
        return bezier

    def pascal_row(n, memo={}):
        # This returns the nth row of Pascal's Triangle
        if n in memo:
            return memo[n]
        result = [1]
        x, numerator = 1, n
        for denominator in range(1, n//2+1):
            # print(numerator,denominator,x)
            x *= numerator
            x /= denominator
            result.append(x)
            numerator -= 1
        if n&1 == 0:
            # n is even
            result.extend(reversed(result[:-1]))
        else:
            result.extend(reversed(result))
        memo[n] = result
        return result
    
    # создание сектора для круга
    def corner(sector, scale, xPos, yPos, dpi):
        scaleL = scaleR = scale
        if sector==1:
            scaleL = -scaleL
            scaleR = -scaleR
        if sector==2:
            scaleR = -scaleR
        if sector==3:
            scaleL = -scaleL
        a = 1.00005519
        b = 0.55342686
        c = 0.99873585

        zz0 = (((0 * scaleL)+xPos) / dpi, ((a * scaleR)+yPos) / dpi)
        zz1 = (((b * scaleL)+xPos) / dpi, ((c * scaleR)+yPos) / dpi)
        zz2 = (((c * scaleL)+xPos) / dpi, ((b * scaleR)+yPos) / dpi)
        zz3 = (((a * scaleL)+xPos) / dpi, ((0 * scaleR)+yPos) / dpi)
        return  zz0, zz1, zz2, zz3

    # создание круга в svg
    def createCircle(drawPath, radius, xPos, yPos, dpi, stroke_width, color):
        
        path = drawSvg.Path(stroke=color, stroke_width=stroke_width, fill='none') 

        p0,p1,p2,p3 = cvDraw.corner(0, radius, xPos, yPos, dpi)
        path.M(p0[0], p0[1])
        path.C(p1[0], p1[1],  p2[0], p2[1],  p3[0], p3[1])

        n3,n2,n1,n0 = cvDraw.corner(2, radius, xPos, yPos, dpi)
        path.C(n1[0], n1[1],  n2[0], n2[1],  n3[0], n3[1])

        m0,m1,m2,m3 = cvDraw.corner(1, radius, xPos, yPos, dpi)
        path.C(m1[0], m1[1],  m2[0], m2[1],  m3[0], m3[1])

        k3,k2,k1,k0 = cvDraw.corner(3, radius, xPos, yPos, dpi)
        path.C(k1[0], k1[1],  k2[0], k2[1],  k3[0], k3[1])
        
        path.Z()

        drawPath.append(path)
        
    # создание контура
    def createContureSvg(lines, draw, path, dpi):
        # dpi =1
        # cvDraw.createSvg(lines, dpi)
        indexMax = len(lines)-1
        # добавление овала 
        if indexMax == 1:
            lineA = lines[0]
            lineB = lines[1]
            
            disp = 5
            lineA[0] = (int(lineA[0][0]+disp),int(lineA[0][1]))
            lineA[1] = (int(lineA[1][0]-disp),int(lineA[1][1]))
            
            lineB[0] = (int(lineB[0][0]-disp),int(lineB[0][1]))
            lineB[1] = (int(lineB[1][0]+disp),int(lineB[1][1]))

            pp0, pp1 = cvDraw.convertToPoint(lineA)
            pp2, pp3 = cvDraw.convertToPoint(lineB)

            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            cvDraw.createHalfCircle(lineA, lineB, path, dpi, False)
            path.L(pp2.x / dpi, pp2.y / dpi).L(pp3.x / dpi, pp3.y / dpi) 
            cvDraw.createHalfCircle(lineB, lineA, path, dpi, False)
            path.Z()
            draw.append(path)
            return
            
        # добавление главного контура
        pp0, pp1, centroid1, centroid2, pp2 = cvDraw.createAngle(lines[indexMax][0], lines[indexMax][1],lines[0][0], lines[0][1])
        # pp0 = None
        if pp0 is not None:
            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
        else:
            lineA = lines[0]
            lineB = lines[indexMax]
            path.M(lineA[0][0] / dpi, lineA[0][1] / dpi)

        for index in range(indexMax):
            lineA = lines[index]
            lineB = lines[index+1]
            typeLine = lineA[2]
            if typeLine == LineStatus.sequest:
                path.L(lineB[1][0] / dpi,lineB[1][1] / dpi) 
                continue
            elif typeLine == LineStatus.parallel:
                # path.L(lineB[0][0] / dpi,lineB[0][1] / dpi) 
                
                # path.L(lineB[0][0] / dpi,lineB[0][1] / dpi) 
                
                # path.L(lineA[1][0] / dpi,lineA[1][1] / dpi) 
                # path.L(lineB[0][0] / dpi,lineB[0][1] / dpi) 
                # cvDraw.aligmintParallel(lineA, lineB)
                cvDraw.createHalfCircle(lineA, lineB, path, dpi, True)
                continue
            else:
                pp0, pp1, centroid1, centroid2, pp2 = cvDraw.createAngle(lineA[0], lineA[1],lineB[0], lineB[1])
                if pp0 is not None:
                    path.L(pp1.x / dpi, pp1.y / dpi) 
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
        path.Z()
        draw.append(path)
        return
    def createSvg(lines, dpi):
        points=[]
        for pp in lines:
            point = Point(pp[0][0] / dpi, pp[0][1] / dpi)
            points.append(point)
            point = Point(pp[1][0] / dpi, pp[1][1] / dpi)
            points.append(point)
            continue
        area = Polygon([i for i in points])
        
        with open('test.svg', 'w') as f:
            f.write('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink= "http://www.w3.org/1999/xlink">')
            f.write(area.svg())
            f.write('</svg>')
            
        return
    def Average(valA, valB):
        val = (valA + valB)/2
        return val
    def deltaLine(line):
        deltaX = abs(line[0][0] - line[1][0])
        deltaY = abs(line[0][1] - line[1][1])
        return deltaX, deltaY
    def aligmentParallel(lineA, lineB):
        deltaX, deltaY = cvDraw.deltaLine(lineA)
        AlgVert = False
        if deltaX < 5: 
            AlgVert = True
        if AlgVert == True:
            averageY1 = cvDraw.Average(lineA[0][1], lineB[1][1])
            averageY2 = cvDraw.Average(lineA[1][1], lineB[0][1])

            averageX1 = cvDraw.Average(lineA[0][0], lineA[1][0])
            averageX2 = cvDraw.Average(lineB[0][0], lineB[1][0])

            # lineA[0] = (int(averageX1),int(averageY1))
            lineA[1] = (int(averageX1),int(averageY2))
            
            lineB[0] = (int(averageX2),int(averageY2))
            # lineB[1] = (int(averageX2),int(averageY1))
        else:
            averageY1 = cvDraw.Average(lineA[0][1], lineB[1][1])
            averageY2 = cvDraw.Average(lineA[1][1], lineB[0][1])
            
        return
    # нахождение отрезка от ближайшей точки из pointA, pointB до intersectionPoint
    def createLineFromInterction(pointA, pointB, intersectionPoint):
        l1 = LineString([pointA, intersectionPoint])
        l2 = LineString([pointB, intersectionPoint])
        l1length = l1.length
        l2length = l2.length
        if l2length < l1length:
            return l2
        return l1
    def cut(line, distance):
        # Cuts a line in two at a distance from its starting point
        if distance <= 0.0 or distance >= line.length:
            return [LineString(line)]
        coords = list(line.coords)
        for i, p in enumerate(coords):
            pd = line.project(Point(p))
            if pd == distance:
                return [
                    LineString(coords[:i+1]),
                    LineString(coords[i:])]
            if pd > distance:
                cp = line.interpolate(distance)
                return [
                    LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]
          
    # вычисление контрольных точек для безье
    def calkControlPoints(lineA, lineB, place):
        pointA0, pointA1 = cvDraw.convertToPoint(lineA)

        pp0s, pp1s = cvDraw.scale(pointA0, pointA1, 30)
        coordsB = lineB.coords
        pp2s, pp3s = cvDraw.scale(Point(coordsB[0][0],coordsB[0][1]), Point(coordsB[1][0],coordsB[1][1]), 30)
        l1 = LineString([pp0s, pp1s])
        l2 = LineString([pp2s, pp3s])
        # пересечение линий
        result = l1.intersection(l2)

        lineResult1 = cvDraw.createLineFromInterction(pointA0,pointA1,result)
        # lineResult1 = lineResult1.centroid

        lineResult2 = cvDraw.createLineFromInterction(coordsB[0],coordsB[1],result)
        # return lineResult1.centroid, result
        
        bez0= cvDraw.divideLine(lineResult1, 0.01)
        bez1= cvDraw.divideLine(lineResult2, 0.01)
        return bez0, bez1
    def divideLine(line, place):
        splitter = MultiPoint([line.interpolate((place), normalized=True) for i in range(1, 2)])
        split(line, splitter).wkt
        return splitter.centroid
    def createHalfCircle(lineA, lineB, path, dpi, isLeft):
        pointA = lineA[1]
        pointB = lineB[0]
        cd_length = cvDraw.distancePoint(pointA, pointB)
        
        # начальная и конечная точка кривой
        startCur = Point(pointA[0],pointA[1])
        finCur = Point(pointB[0],pointB[1])
        ab = LineString([startCur, finCur])
        dir = 'left'
        if isLeft == False:
            dir = 'right'
        # сдвиг на половину длины
        shiftedLine  = ab.parallel_offset(cd_length / 2, dir)
                                     
        centroid = shiftedLine.centroid.coords
        xCenter = centroid[0][0]
        yCenter = centroid[0][1]
        # получение контрольных точек для кривой безье
        # coordsA  = shiftedLine.coords 
        # start = coordsA[0]
        # fin = coordsA[1]
        
        bezP1, bezP2 = cvDraw.calkControlPoints(lineA, shiftedLine, 0.01)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, xCenter / dpi, yCenter / dpi)

        bezP1, bezP2 = cvDraw.calkControlPoints(lineB, shiftedLine, 0.01)
        path.C(bezP2.x / dpi, bezP2.y / dpi, bezP1.x / dpi, bezP1.y / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        # path.C(start[0] / dpi, start[1] / dpi, start[0] / dpi, start[1] / dpi, xCenter / dpi, yCenter / dpi)
        # path.C(fin[0] / dpi, fin[1] / dpi, fin[0] / dpi, fin[1] / dpi, lineB[0][0] / dpi,lineB[0][1] / dpi)

        return
    # создание зхакругления для контура
    # если Nont то паралельны
    def createAngle(pointA, pointB,pointC, pointD):
        distAC = cvDraw.distancePoint(pointA, pointC) 
        distAD = cvDraw.distancePoint(pointA, pointD)
        distBC = cvDraw.distancePoint(pointB, pointC)
        distBD = cvDraw.distancePoint(pointB, pointD)
        
        a = np.array([distAC,distAD,distBC,distBD])
        index = np.where(a == a.min())[0][0]
        point0 = None
        point1 = None
        point2 = None
        point3 = None
        if index == 1:
            point0 = pointB
            point1 = pointA
            point2 = pointD
            point3 = pointC
        elif index == 2:
            point0 = pointA
            point1 = pointB
            point2 = pointC
            point3 = pointD
        elif index == 0:
            point0 = pointA
            point1 = pointB
            point2 = pointC
            point3 = pointD
        else:
            zz=0
            
        pp0 = Point(point0[0],point0[1])
        pp1 = Point(point1[0],point1[1])
        pp2 = Point(point2[0],point2[1])
        pp3 = Point(point3[0],point3[1])
        
        pp0s, pp1s = cvDraw.scale(pp0, pp1, 30)
        pp2s, pp3s = cvDraw.scale(pp2, pp3, 30)

        l1 = LineString([pp0s, pp1s])
        l2 = LineString([pp2s, pp3s])
        result = l1.intersection(l2)
        testOut = str(result)
        if testOut.find("EMPTY") >= 0 or testOut.find("LINE") >= 0:
            return None, None, None, None, None

        # poly = Polygon([pp0,pp1,pp2,pp3])
        # containt = poly.contains(result)
        # if containt == False:
        #     return None, None, None, None, None
        # boundary = poly.boundary
        
        l3 = LineString([pp1, result])
        l4 = LineString([pp2, result])

        centroid1 = l3.centroid
        centroid2 = l4.centroid
        return pp0, pp1, centroid1, centroid2, pp2

    def is_eql(a_delta, b_delta, dist):
        dist = 10
        if b_delta > a_delta - dist and b_delta < a_delta + dist:
            return True
        return False
    def is_parallel(line1, line2):
        a_delta_x = abs(line1[1][0] - line1[0][0])
        a_delta_y = abs(line1[1][1] - line1[0][1])
        b_delta_x = abs(line2[1][0] - line2[0][0])
        b_delta_y = abs(line2[1][1] - line2[0][1])
        
        eq0 = cvDraw.is_eql(a_delta_x, b_delta_x, 4)
        eq1 = cvDraw.is_eql(a_delta_y, b_delta_y, 4)
        # if a_delta_x * b_delta_y == a_delta_y * b_delta_x:
        if eq0 == True or eq1 == True:
            return True 
        else:
            return False 
    
    def Add(firstPoint, secondPoint, addFactor):
        x2 = firstPoint.x +(secondPoint.x - firstPoint.x) + addFactor
        y2 = firstPoint.y +(secondPoint.y - firstPoint.y) + addFactor
        secondPoint = Point(x2, y2)
        return secondPoint
    def convertToPoint(line):
        p0 = Point(line[0][0],line[0][1])
        p1 = Point(line[1][0],line[1][1])
        return p0, p1
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
    def distancePoint(pointA, pointB):
        deltaX = pointA[0]-pointB[0]
        deltaY = pointA[1]-pointB[1]
        lenLine = math.sqrt( (deltaX**2)+(deltaY**2))
        return lenLine
