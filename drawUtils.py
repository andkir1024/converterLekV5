import cv2
import numpy as np
import math
import drawsvg as drawSvg
import enum
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
# from shapely.centerline import Centerlinefrom 



class LineStatus(enum.Enum):
    round = 0
    sequest = 1
    parallel = 2
    undefined = 3
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
    
    # вырезаем короткие линии
    def packLine( last_point, curr_point, border, index):
        x1=int(last_point[0])
        y1=int(last_point[1])
        x2=int(curr_point[0])
        y2=int(curr_point[1])
        lenLine = math.sqrt( ((x1-x2)**2)+((y1-y2)**2))
        if lenLine > border:
            # 0 кордината начальной точки
            # 1 кордината конечной
            # 2 статус
            # 3 длина линии
            # 4 индекс точки
            # 5 расстоячние до следующей точки
            return  [(x1, y1), (x2, y2), LineStatus.undefined, lenLine, index, 0]
        return None
    
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
    def createCircle(drawPath, radius, xPos, yPos, dpi = 96.0):
        
        path = drawSvg.Path(stroke='blue', stroke_width=5, fill='none') 

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
    def createConture(lines, draw, path, dpi):
        # cvDraw.createSvg(lines, dpi)
        # добавление главного контура
        indexMax = len(lines)-1
        pp0, pp1, centroid1, centroid2, pp2 = cvDraw.createAngle(lines[indexMax][0], lines[indexMax][1],lines[0][0], lines[0][1])
        if pp0 is not None:
            path.M(pp0.x / dpi, pp0.y / dpi).L(pp1.x / dpi, pp1.y / dpi) 
            path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)

        all=0        
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
                cvDraw.createHalfCircle(lineA, lineB, path, dpi)
                continue
            else:
                pp0, pp1, centroid1, centroid2, pp2 = cvDraw.createAngle(lineA[0], lineA[1],lineB[0], lineB[1])
                if pp0 is not None:
                    # cvDraw.createHalfCircle(lineA, lineB)
                # else:
                    path.L(pp1.x / dpi, pp1.y / dpi) 
                    path.C(centroid1.x / dpi, centroid1.y / dpi, centroid2.x / dpi,centroid2.y / dpi, pp2.x / dpi, pp2.y / dpi)
            all = all +1
            # if all > 1:
                # break 
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

    def createHalfCircle(lineA, lineB, path, dpi):
        pointA = lineA[1]
        pointB = lineB[0]
        cd_length = cvDraw.distancePoint(pointA, pointB)
        pp0 = Point(pointA[0],pointA[1])
        pp1 = Point(pointB[0],pointB[1])
        ab = LineString([pp0, pp1])
        # centroid = ab.centroid.coords

        left  = ab.parallel_offset(cd_length / 2, 'left')
        right = ab.parallel_offset(cd_length / 2, 'right')
        centroid = left.centroid.coords
        # centroid = right.centroid.coords

        x= centroid[0][0]
        y= centroid[0][1]
        # y= centroid[0][1] + cd_length
        path.L(x / dpi, y / dpi) 
        # path.L(centroid[0][0] / dpi, centroid[0][1] / dpi) 
        path.L(lineB[0][0] / dpi,lineB[0][1] / dpi) 

        return
        
        pp0 = Point(pointA[0],pointA[1])
        pp1 = Point(pointB[0],pointB[1])
        ab = LineString([pp0, pp1])
        centroid = ab.centroid
        left  = ab.parallel_offset(cd_length / 2, 'left')
        right = ab.parallel_offset(cd_length / 2, 'right')
        l= left.coords
        r= right.coords
        path.M(l[0][0] / dpi,l[0][1] / dpi) 
        path.L(r[1][0] / dpi,r[1][1] / dpi) 
        

        # a = (10, 20)
        # b = (15, 30)
        # cd_length = 6

        # ab = LineString([a, b])
        # left = ab.parallel_offset(cd_length / 2, 'left')
        # right = ab.parallel_offset(cd_length / 2, 'right')
        # c = left.boundary
        # d = right.boundary  # note the different orientation for right offset
        # cd = LineString([c, d])


        # distAC = cvDraw.distancePoint(pointA, pointB) 
        
        # polygon = Polygon([pp0, pp1])

        # centerline = Centerline(polygon, **attributes)        
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
        
        l3 = LineString([pp1, result])
        l4 = LineString([pp2, result])

        centroid1 = l3.centroid
        centroid2 = l4.centroid
        return pp0, pp1, centroid1, centroid2, pp2
    def Add(firstPoint, secondPoint, addFactor):
        x2 = firstPoint.x +(secondPoint.x - firstPoint.x) + addFactor
        y2 = firstPoint.y +(secondPoint.y - firstPoint.y) + addFactor
        secondPoint = Point(x2, y2)
        return secondPoint
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
        