import cv2
import numpy as np
import math
import drawsvg as drawSvg

class cvDraw:
    def show_testImage(nameImage, container, scale):
        # afterL = cv2.imread(nameImage)
        # afterLimg = cv2.resize(afterL, (0, 0), interpolation=cv2.INTER_LANCZOS4, fx=scale, fy=scale)
        # rmain1Add = Image.fromarray(afterLimg)
        # rmain1tkAdd = ImageTk.PhotoImage(image=rmain1Add)
        # container.imgtk = rmain1tkAdd
        # container.configure(image=rmain1tkAdd)
        return

    def readImage( imgName, title):
        img = cv2.imread(imgName);  # tecno camon 19 pro (997x1280)(Размеры 166.8x74.6)
        w, h = img.shape[:2]
        title = title + (f'  viewBox h: {w} w: {h}')
        root.title(title)
        return img

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
    
    def packLine( last_point, curr_point, border = 100):
        # if len(last_point) == 1:
            # return None
        x1=int(last_point[0])
        y1=int(last_point[1])
        x2=int(curr_point[0])
        y2=int(curr_point[1])
        lenLine = math.sqrt( ((x1-x2)**2)+((y1-y2)**2))
        if lenLine > border:
            return  [(x1, y1), (x2, y2)]
        return None
    
    def angleLine( line):
        deltaX = abs(line[0][0] - line[1][0])
        deltaY = abs(line[0][1] - line[1][1])
        if cvDraw.testAngle( deltaX ) is None:
            return "v"
        if cvDraw.testAngle( deltaY ) is None:
            return "h"
        return deltaX / deltaY
    
    def testAngle( angle ):
        if angle < 10:
            return None
        return angle    
    
    def calkSize( countour ):
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
    def corner(sector, scale, xPos, yPos):
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

        zz0 = ((0 * scaleL)+xPos, (a * scaleR)+yPos)
        zz1 = ((b * scaleL)+xPos, (c * scaleR)+yPos)
        zz2 = ((c * scaleL)+xPos, (b * scaleR)+yPos)
        zz3 = ((a * scaleL)+xPos, (0 * scaleR)+yPos)
        return  zz0, zz1, zz2, zz3

    # создание круга в svg
    def createCircle(drawPath, radius, xPos, yPos):
        path = drawSvg.Path(stroke='blue', stroke_width=5, fill='none') 

        p0,p1,p2,p3 = cvDraw.corner(0, radius, xPos, yPos)
        path.M(p0[0], p0[1])
        path.C(p1[0], p1[1],  p2[0], p2[1],  p3[0], p3[1])

        n3,n2,n1,n0 = cvDraw.corner(2, radius, xPos, yPos)
        path.C(n1[0], n1[1],  n2[0], n2[1],  n3[0], n3[1])

        m0,m1,m2,m3 = cvDraw.corner(1, radius, xPos, yPos)
        path.C(m1[0], m1[1],  m2[0], m2[1],  m3[0], m3[1])

        k3,k2,k1,k0 = cvDraw.corner(3, radius, xPos, yPos)
        path.C(k1[0], k1[1],  k2[0], k2[1],  k3[0], k3[1])
        
        path.Z()

        drawPath.append(path)
        