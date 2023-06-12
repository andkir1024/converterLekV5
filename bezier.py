import enum
import os
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from mathUtils import *
# from scipy import interpolate

class bezier:
    def is_eql(a_delta, b_delta, dist):
        if b_delta < dist and a_delta < dist:
            return True
        return False
    def is_eqlVal(a_val, b_val, dist):
        delta = (a_val - b_val)
        if delta < dist:
            return True
        return False
    def findVertInFig(figure):
        xL=10000 
        xR=0
        posXL = None
        posXR = None
        for fig in figure:
            len = fig[3]
            dY = abs(fig[0][1]-fig[1][1])
            if len > 10:
                if dY < xL:
                    xL=dY
                    posXL = fig[0][0]
                if dY > xR:
                    xR=dY
                    posXR = fig[0][0]
        return posXL, posXR
    def testFig2(lineA, lineB, corner, path, dpi):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        
        figure = corner.linesFig
        if figure != None:
            posXL, posXR = bezier.findVertInFig(figure)
            if posXL is not None and posXR is not None:
                corner.minX = posXL
                corner.maxX = posXR
                # corner.minX = 1267
                # corner.maxX = 1374
        xCenter = corner.minX + ((corner.maxX - corner.minX)/2)
        yCenter = corner.minY + ((corner.maxY - corner.minY)/2)
        dX = pp2.x - pp1.x
        radius = dX / 2

        coff0 = 0.5
        coff1 = 0.2
        # part1
        pA = Point(corner.minX,corner.minY)
        pB = Point(corner.minX,corner.maxY-radius)
        pC = Point(corner.minX,corner.maxY)
        pD = Point(xCenter,corner.maxY)
        pE = Point(corner.maxX,corner.maxY)
        pF = Point(corner.maxX,corner.maxY-radius)
        pG = Point(corner.maxX,corner.minY)

        path.L(pA.x / dpi, pA.y / dpi) 
        path.L(pB.x / dpi, pB.y / dpi) 
        
        # path.L(pC.x / dpi, pC.y / dpi) 
        # path.L(pD.x / dpi, pD.y / dpi) 
        bezier.doCorner(pB, pC, pD, path, dpi, 0.7, 0.3)

        # path.L(pE.x / dpi, pE.y / dpi) 
        # path.L(pF.x / dpi, pF.y / dpi) 
        bezier.doCorner(pD, pE, pF, path, dpi, 0.7, 0.3)

        path.L(pG.x / dpi, pG.y / dpi) 

        return True 
    def doCorner(pA, pB, pC, path, dpi, coff0, coff1):
        bezP1 = bezier.interpolatePoint(pA, pB, coff0)
        bezP2 = bezier.interpolatePoint(pB, pC, coff1)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
        return
    # S фигура подготовка
    def prepareS(lineA, lineB, corner):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        xCenter = corner.minX + ((corner.maxX - corner.minX)/2)
        yCenter = corner.minY + ((corner.maxY - corner.minY)/2)
        deltaX = lineA[0][0]-lineA[1][0]
        # deltaY = lineA[0][1]-lineA[1][1]
        # if deltaY == 0:
        #     deltaY = 1
        prop = abs((corner.maxX - corner.minX)/(corner.maxY - corner.minY))
        return xCenter,yCenter,deltaX,prop
    # S фигура сверху вниз
    def doSUpDown(xCenter,yCenter, corner, path, dpi, coff0, coff1, dir, prop):
        pA = Point(corner.minX,corner.minY)
        pB = Point(xCenter,corner.minY)
        pC = Point(xCenter,yCenter)
        pD = Point(xCenter,corner.maxY)
        pE = Point(corner.maxX,corner.maxY)
        mode = 0
        if prop > 0.9 and prop < 1.1:
            mode = 1
            coff0 = 0.4
            coff1 = 0.2
        if dir == False:
            pA, pE = pE, pA
            pB, pD = pD, pB
        path.L(pA.x / dpi, pA.y / dpi) 
        bezP1 = bezier.interpolatePoint(pA, pB, coff0)
        bezP2 = bezier.interpolatePoint(pB, pC, 1-coff1)
        # bezP2 = bezier.interpolatePoint(pA, pC, 0.5)
        if mode == 1:
            bezP2 = bezP1
        # bezP2 = Point(bezP1.x,bezP2.y)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
        
        bezP1 = bezier.interpolatePoint(pC, pD, coff1)
        # bezP1 = bezier.interpolatePoint(pC, pE, 0.5)
        bezP2 = bezier.interpolatePoint(pD, pE, 1-coff0)
        if mode == 1:
            bezP1 = bezP2
        # bezP1.x = bezP2.x
        # bezP1 = Point(bezP2.x,bezP1.y)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
        return
    # S фигура снизу вверх
    def doSDownUp(xCenter,yCenter, corner, path, dpi, coff0, coff1, dir):
        pA = Point(corner.minX,corner.maxY)
        pB = Point(xCenter,corner.maxY)
        pC = Point(xCenter,yCenter)
        pD = Point(xCenter,corner.minY)
        pE = Point(corner.maxX,corner.minY)
        if dir == False:
            pA, pE = pE, pA
            pB, pD = pD, pB

        path.L(pA.x / dpi, pA.y / dpi) 
        bezP1 = bezier.interpolatePoint(pA, pB, coff0)
        bezP2 = bezier.interpolatePoint(pB, pC, coff1)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
        
        bezP1 = bezier.interpolatePoint(pC, pD, 0.8)
        bezP2 = bezier.interpolatePoint(pD, pE, 0.2)
        # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
        path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
        return
    # тестирование горизонтальные линии последовательно
    def testFig1(lineA, lineB, corner, path, dpi):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        xCenter = corner.minX + ((corner.maxX - corner.minX)/2)
        yCenter = corner.minY + ((corner.maxY - corner.minY)/2)
            
        deltaX = pp0.x-pp1.x
        deltaY = pp1.y-pp2.y
        coff0 = 0.5
        coff1 = 0.2
        # слева направо
        if deltaX > 0: 
            path.L(pp0.x / dpi, pp0.y / dpi) 
            path.L(pp1.x / dpi, pp1.y / dpi) 
            path.L(pp2.x / dpi, pp2.y / dpi) 
            path.L(pp3.x / dpi, pp3.y / dpi) 
        # справа налево
        else:
            if deltaY < 0:
                pA = Point(corner.minX,corner.minY)
                pB = Point(xCenter,corner.minY)
                pC = Point(xCenter,yCenter)
                pD = Point(xCenter,corner.maxY)
                pE = Point(corner.maxX,corner.maxY)

                path.L(pA.x / dpi, pA.y / dpi) 
                bezP1 = bezier.interpolatePoint(pA, pB, coff0)
                bezP2 = bezier.interpolatePoint(pB, pC, coff1)
                # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
                path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
                
                bezP1 = bezier.interpolatePoint(pC, pD, 0.8)
                bezP2 = bezier.interpolatePoint(pD, pE, 0.2)
                # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
                path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
            else:
                pA = Point(corner.minX,corner.maxY)
                pB = Point(xCenter,corner.maxY)
                pC = Point(xCenter,yCenter)
                pD = Point(xCenter,corner.minY)
                pE = Point(corner.maxX,corner.minY)

                path.L(pA.x / dpi, pA.y / dpi) 
                bezP1 = bezier.interpolatePoint(pA, pB, coff0)
                bezP2 = bezier.interpolatePoint(pB, pC, coff1)
                # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pC.x / dpi, pC.y / dpi)
                path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pC.x / dpi, pC.y / dpi)
                
                bezP1 = bezier.interpolatePoint(pC, pD, 0.8)
                bezP2 = bezier.interpolatePoint(pD, pE, 0.2)
                # path.L(bezP1.x / dpi, bezP1.y / dpi).L(bezP2.x / dpi, bezP2.y / dpi).L( pE.x / dpi, pE.y / dpi)
                path.C(bezP1.x / dpi, bezP1.y / dpi, bezP2.x / dpi, bezP2.y / dpi, pE.x / dpi, pE.y / dpi)
        return True 
    # тестирование вертикальые линии последовательно
    def testFig0(lineA, lineB, lineC, path, dpi):
        pp0, pp1 = bezier.convertToPoint(lineA)
        pp2, pp3 = bezier.convertToPoint(lineB)
        sY = pp1.y
        fY = pp2.y
        eqVert = bezier.is_eqlVal(sY, fY, 4)
        deltaY1 = pp1.y-pp0.y
        deltaY2 = pp3.y-pp2.y
        deltaX = pp1.x-pp2.x
        sign = deltaY1 * deltaY2
        if eqVert == True  and sign >= 0:
            if deltaX > 0:
                path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp1.y / dpi) 
            else:
                path.L(pp1.x / dpi, pp2.y / dpi).L(pp2.x / dpi, pp2.y / dpi) 
            # path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp1.y / dpi) 
            # path.L(pp1.x / dpi, pp1.y / dpi).L(pp2.x / dpi, pp2.y / dpi) 
            return True
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
    def get_angleP(pointS, pointE) -> float:
        'Returns the angle (in radians) of a given line in relation with the X axis.'
        # start, end = line.boundary
        start, end = Point(pointS),Point(pointE)
        if end.y - start.y == 0:  # Avoids dividing by zero.
            return math.acos(0)
        return -math.atan((end.x - start.x) / (end.y - start.y))

    def resize_line(line: LineString, length: float) -> LineString:
        'Returns a new line with the same center and angle of a given line, but with different length.'
        if len(line.coords) == 0:
            return None

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
    def convertToPoint(line):
        p0 = Point(line[0][0],line[0][1])
        p1 = Point(line[1][0],line[1][1])
        return p0, p1
    def aligmentHor(pp0, pp1):
        y = pp0.y + ((pp1.y - pp0.y)/2)
        return Point(pp0.x, y), Point(pp1.x, y)
    def aligmentVert(pp0, pp1):
        x = pp0.x + ((pp1.x - pp0.x)/2)
        return Point(x, pp0.y), Point(x, pp1.y)
    def is_parallel(line1, line2,minX,minY,maxX,maxY,linesFig ):
        a_delta_x = abs(line1[1][0] - line1[0][0])
        a_delta_y = abs(line1[1][1] - line1[0][1])
        b_delta_x = abs(line2[1][0] - line2[0][0])
        b_delta_y = abs(line2[1][1] - line2[0][1])
class FigureStatus(enum.Enum):
    smoothCorner = 1
    undefined = 2
    halfCircleUp = 3
    halfCircleDown = 4
    sUpDown = 5
    sDownUp = 6
    
class contoureAnalizer:
    counterCorner = 0 
    curveDir = "./out/"
    def start():
        contoureAnalizer.counterCorner=0
        
        for f in os.listdir(contoureAnalizer.curveDir):
            os.remove(os.path.join(contoureAnalizer.curveDir, f))        
    def getParamVector(pointS, pointF):
        deltax = pointS[0] - pointF[0]
        deltay = pointS[1] - pointF[1]
        len = math.sqrt(deltax**2+deltay**2)
        rad = bezier.get_angleP(Point(pointS[0],pointS[1]),Point(pointF[0],pointF[1]))
        angle = math.degrees(rad)
        return  (int(len), int(angle))
    def drawCountureFromLine(lineA, lineB):
        contours = lineA[6].pointsFig.copy()
        type = FigureStatus.undefined
        if contours is not None:
            shape = contours.shape
            xMin = yMin = 10000000
            xMax = yMax = 0
            for index in range(len(contours)):
                contour = contours[index]
                x = contour[0]
                y = contour[1]
                
                xMin = min(xMin,x)
                yMin = min(yMin,y)
                xMax = max(xMax,x)
                yMax = max(yMax,y)
                
            for contour in contours:
                contour[0]=contour[0]-xMin
                contour[1]=contour[1]-yMin
            w = xMax-xMin
            h = yMax-yMin
            th = 3 if w<100 else 10
            img = np.empty([h,w*3, 3], dtype=np.uint8) 
            # img = np.empty([w*2,h*2, 3], dtype=np.uint8) 
            img.fill(0) # gray            
            peri = cv2.arcLength(contours,True)
            
            # contoureAnalizer.drawSingleCounture(img, contours,  0.005 * peri, w*1, (255,255,255),th)
            typeFigure = contoureAnalizer.drawSingleCounture(img, contours,  0.01 * peri, w*1, (255,255,255),th,w,h,lineA, lineB)

            # contoureAnalizer.drawSingleCounture(img, contours,  0.001 * peri, w*0, (255,255,255),th)
            # contoureAnalizer.drawSingleCounture(img, contours,  0.01 * peri, w*1, (255,255,0),th)
            # contoureAnalizer.drawSingleCounture(img, contours,  0.1 * peri, w*2, (255,255,0),th)
            name = contoureAnalizer.curveDir + str(contoureAnalizer.counterCorner) + ".png"
            contoureAnalizer.counterCorner+=1
            cv2.imwrite(name, img) 
        return (typeFigure,lineA, lineB)
    def drawSingleCounture(img, contoursSrc, coff, xstart, color, th,w,h,lineA, lineB):
        contours = contoursSrc.copy()
        for contour in contours:
            contour[0]=contour[0]+xstart
        approx = cv2.approxPolyDP(contours, coff, False)
        
        diffs = []
        for index in range(len(approx)-1):
            contour = approx[index]
            contourNext = approx[index+1]
            diffs.append(contoureAnalizer.getParamVector(contour[0],contourNext[0]))
        
        cv2.drawContours(img, approx, -1, color, th, cv2.LINE_AA)
        cv2.polylines(img, [approx], False, (0, 255, 0), 3)
        typeFigure = contoureAnalizer.clasificatorFigure(diffs, approx, w, h,lineA, lineB)
        if w < 32 and h < 32:
            return FigureStatus.smoothCorner
        return typeFigure
    def clasificatorFigure(diffs, countor, w, h,lineA, lineB):
        someSign= contoureAnalizer.check_sort(diffs)
        analized = mathSvg.testSequence(diffs)
        if mathSvg.isHalfCircle(analized) == True:
            return FigureStatus.halfCircleUp
        sFig = mathSvg.isSFigure(analized, diffs,countor)
        if sFig == 1:
            return FigureStatus.sDownUp
        if sFig == -1:
            return FigureStatus.sUpDown


        # val0= contoureAnalizer.isSorted(diffs, 1)
        # val1= contoureAnalizer.isSorted(diffs, -1)
        # if len(diffs) == 8:
            # return FigureStatus.halfCircleUp
        if someSign:
            return FigureStatus.smoothCorner
        return FigureStatus.undefined
    
    def check_sort(array):
        # plus = all([x > y for x, y in zip(array, array[1:])])
        indices = [1]
        out = np.take(array, indices, axis=1)        
        plus = all([x > y for x, y in zip(out, out[1:])])
        return plus
    
    def isSorted(x,flag):
        st = x[0][1]
        delta = []
        for index in range(1, len(x)):
            test = x[index][1]
            delta.append( test - st)
            st = test 
        return
    def sign(a):
        if a>0:
            return 1;
        elif a<0:
            return -1;
        else:
            return 0    
    