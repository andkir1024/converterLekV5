import cv2
import numpy as np
import math
from drawUtils import cvDraw
import drawsvg as drawSvg
from shapely import Point
# from shapely import *
import svgwrite

class cvUtils:
    def findLines(img_grey, img_Draw, draw_conrure):
        return
        # rho = 1  # distance resolution in pixels of the Hough grid
        # theta = np.pi / 180  # angular resolution in radians of the Hough grid
        # threshold = 15  # minimum number of votes (intersections in Hough grid cell)
        # min_line_length = 50  # minimum number of pixels making up a line
        # max_line_gap = 40  # maximum gap in pixels between connectable line segments

        # # Run Hough on edge detected image
        # # Output "lines" is an array containing endpoints of detected line segments
        # lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]),min_line_length, max_line_gap)
        # return lines
        # lines = cv2.HoughLines(img_grey, rho = 1, theta = 1 * np.pi/180, threshold=120, srn=0, stn = 0, min_theta=1, max_theta=2)
        lines = cv2.HoughLinesP(img_grey, rho = 1, theta = np.pi/180, threshold = 5, minLineLength= 500, maxLineGap=40)

        # lines = cv2.HoughLines(img_grey, rho = 1, theta = 1 * np.pi/180, threshold=120, srn=0, stn = 0, min_theta=1, max_theta=2)

        for i in range(0, len(lines)):
            rho, theta = lines[i][0][0], lines[i][0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(img_Draw, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
    def findCircles(img_grey, img_Draw, draw_conrure):
        rows = img_grey.shape[0]
        circles = cv2.HoughCircles(img_grey, cv2.HOUGH_GRADIENT, 1, rows / (64),
                                param1=160, param2=80,
                                # param1=160, param2=110,
                                # param1=40, param2=40,
                                # param1=200, param2=10,
                                # param1=100, param2=30,
                                minRadius=3, maxRadius=1000)            
        if draw_conrure == True:
            if circles is not None :
                circlesDraw = np.uint16(np.around(circles))
                for i in circlesDraw[0, :]:
                    center = (i[0], i[1])
                    # circle center
                    # cv2.circle(img_Draw, center, 1, (0, 100, 100), 3)
                    # circle outline
                    radius = i[2]
                    cv2.circle(img_Draw, center, radius, (255, 0, 255), 2)
        return circles
    def findCircles2(img_grey, img_Draw, draw_conrure):
        # detector = cv2.SimpleBlobDetector()
        # keypoints = detector.detect(img_grey)
    	# detector = cv2.SimpleBlobDetector_create(params)
        # m_with_keypoints = cv2.drawKeypoints(img_Draw, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 10
        params.maxThreshold = 200


        # Filter by Area.
        params.filterByArea = False
        params.minArea = 15

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.2

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.87
            
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        # Create a detector with the parameters
        ver = (cv2.__version__).split('.')
        if int(ver[0]) < 3 :
            detector = cv2.SimpleBlobDetector(params)
        else : 
            detector = cv2.SimpleBlobDetector_create(params)


        # Detect blobs.
        keypoints = detector.detect(img_Draw)

        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
        # the size of the circle corresponds to the size of blob

        img_Draw = cv2.drawKeypoints(img_Draw, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
     
        return
    def getContours1(imgGray, img,cThr=[100,100],showCanny=False,minArea=0,filter=0,draw =True):
        d = drawSvg.Drawing(200, 100, origin='center')
        # imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
        kernel = np.ones((5,5))
        imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
        imgThre = cv2.erode(imgDial,kernel,iterations=3)
        if showCanny:cv2.imshow('Canny',imgCanny)
        # contours,hiearchy = cv2.findContours(imgThre,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # imgCanny = imgGray
        contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        finalCountours = []
        for i in contours:
            area = cv2.contourArea(i)
            if area > minArea:
                peri = cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,0.02*peri,True)
                bbox = cv2.boundingRect(approx)
                finalCountours.append([len(approx),area,approx,bbox,i])
                
        max=0                
        sel_countour=None
        for countour in contours:
            if countour.shape[0]>max:
                sel_countour=countour
                max=countour.shape[0]
                
        last_point=None
        for point in sel_countour:
            curr_point=point[0]
            if not(last_point is None):
                cvDraw.testLine(img, last_point,curr_point, 10)
            last_point=curr_point
        cvDraw.testLine(img, last_point,sel_countour[0][0], 10)
    
        # approx = cv2.approxPolyDP(contours[1],0.2,True)
        # cv2.drawContours(img,contours[1],-1,(255,0,0),16)
        # cv2.drawContours(img,[approx],-1,(0,255,0),6)
        if draw:
            for con in finalCountours:
                approx = cv2.approxPolyDP(con[4],0.2,True)
                # cv2.drawContours(img,con[4],-1,(255,0,0),16)
                # cv2.drawContours(img,[approx],-1,(0,255,0),6)
                # cv2.drawContours(img,con[4],-1,(0,255,0),16)
                
# Draw arrows
        # arrow = drawSvg.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
        # arrow.append(drawSvg.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='red', close=True))
        p = drawSvg.Path(stroke='red', stroke_width=1, fill='none')  # Add an arrow to the end of a path
        p.M(0, 0).C(50, 0, 100,50,100,100)  # Chain multiple path commands
        d.append(p)
        # d.append(drawSvg.Line(30, 20, 0, 10,
                # stroke='red', stroke_width=2, fill='none',
                # marker_end=arrow))  # Add an arrow to the end of a line

        # d.set_pixel_scale(2)  # Set number of pixels per geometry unit
        #d.set_render_size(400, 200)  # Alternative to set_pixel_scale
        # d.save_svg('example.svg')                
        # d.save_png('example.png')
        return img, finalCountours
    def getContours(imgGray, img,cThr=[100,100],showCanny=False,minArea=0,filter=0,draw =True):
        # imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
        kernel = np.ones((5,5))
        imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
        imgThre = cv2.erode(imgDial,kernel,iterations=3)
        # imgCanny = imgGray
        # if showCanny:cv2.imshow('Canny',imgCanny)
        # contours,hiearchy = cv2.findContours(imgThre,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # imgCanny = imgGray
        # contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        finalCountours = []
        for i in contours:
            area = cv2.contourArea(i)
            if area > minArea:
                peri = cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,0.02*peri,True)
                bbox = cv2.boundingRect(approx)
                if filter > 0:
                    if len(approx) == filter:
                        finalCountours.append([len(approx),area,approx,bbox,i])
                else:
                    finalCountours.append([len(approx),area,approx,bbox,i])
        # finalCountours = sorted(finalCountours,key = lambda x:x[1] ,reverse= True)
        if draw:
            for con in finalCountours:
                cv2.drawContours(img,con[4],-1,(0,255,255),6)
        return img, finalCountours
    def reorder(myPoints):
        #print(myPoints.shape)
        myPointsNew = np.zeros_like(myPoints)
        myPoints = myPoints.reshape((4,2))
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        diff = np.diff(myPoints,axis=1)
        myPointsNew[1]= myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew
    def warpImg (img,points,w,h,pad=20):
        # print(points)
        points =reorder(points)
        pts1 = np.float32(points)
        pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        imgWarp = cv2.warpPerspective(img,matrix,(w,h))
        imgWarp = imgWarp[pad:imgWarp.shape[0]-pad,pad:imgWarp.shape[1]-pad]
        return imgWarp
    def findDis(pts1,pts2):
        return ((pts2[0]-pts1[0])**2 + (pts2[1]-pts1[1])**2)**0.5
    def custom_key(extCtr):
        return extCtr[1]
    def sort_contures(contours):
        contours.sort(key=custom_key, reverse=True)
        return
    # выделение главного контура телефона
    def detect_main_conture(aligmentedImgGrayBase, minArea):
        '''
        aligmentedImgGray1 = lekaloFilter.doPrepareFrameV_GetMainContur(aligmentedImgGray)
        # aligmentedImgGray = lekaloFilter.doPrepareFrameV_0(aligmentedImgGray, current_value1, current_value2, clipLimit, tileGridSize)
        aligmentedImgGray2 = lekaloFilter.doPrepareFrameV_1(aligmentedImgGray1, current_value1, current_value2, clipLimit, tileGridSize)
        # aligmentedImgGray1 = cv2.bilateralFilter(aligmentedImgGray1, 19, 75, 75)
        aligmentedImgGray = aligmentedImgGray2.copy()
        '''
        # aligmentedImgGray = lekaloFilter.adaptiveTresholdContur(aligmentedImgGrayBase, 5)
        aligmentedImgGray = cv2.adaptiveThreshold(aligmentedImgGrayBase, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
        clahe = cv2.createCLAHE(clipLimit=0.2, tileGridSize=(8, 8))
        # aligmentedImgGray = clahe.apply(aligmentedImgGrayBase)
        # img = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2RGB)
        # img3 = cv2.equalizeHist(imgGray)

        # aligmentedImgGray = lekaloFilter.doPrepareFrameV_0(aligmentedImgGray, current_value1, current_value2, clipLimit, tileGridSize)
        # aligmentedImgGray = lekaloFilter.cannyContur(aligmentedImgGray, 200)

        objects_contours  = detect_contures_for_mainConture(aligmentedImgGray, minArea)

        aligmentedImgColor = cv2.cvtColor(aligmentedImgGray, cv2.COLOR_GRAY2RGB)
        # lekaloDraw.drawContures(contoursAll, aligmentedImgColor, 4)
        # lekaloDraw.drawContures(objects_contours, aligmentedImgColor, 4)
        # cv2.imwrite('and.png',aligmentedImgColor)

        # zz =objects_contours is None

        allContures = len(objects_contours)
        if allContures > 0:
            return objects_contours[0][0], aligmentedImgGray
        return None, aligmentedImgGray
    def detect_contures(aligmentedImgGray, minArea = 10000, maxArea = 100000000):
        mask = aligmentedImgGray.copy()
        # mask = cv2.GaussianBlur(mask,(15,15),0)
        mask = cv2.bilateralFilter(mask, 19, 75, 75)

        kernel = np.ones((5, 5), np.float32) / 25
        # mask = cv2.filter2D(mask, -1, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS )
        # contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE  )

        objects_contours = prepareContours(contours, minArea, maxArea)

        lines = findLines(mask)
        # circles = findCircles(mask)
        return objects_contours, mask, lines, contours
    def prepareContours(contours, minArea, maxArea):
        objects_contours = []
        for cnt in contours:
            areaLen = cv2.arcLength(cnt, False)
            area = cv2.contourArea(cnt)
            if cnt.size <= 4:
                continue
            # if area > minArea and area < maxArea:
            if area > minArea and area < maxArea:
                extCtr = (cnt,area)
                objects_contours.append(extCtr)
        # objtours = sorted(objects_contours, key=cv2.contourArea)[-1]
        objects_contours.sort(key=custom_key, reverse=True)
        return objects_contours
    def detect_contures_for_mainConture(aligmentedImgGray, minArea = 10000, maxArea = 100000000):
        mask = aligmentedImgGray.copy()
        # mask = cv2.GaussianBlur(mask,(15,15),0)
        mask = cv2.bilateralFilter(mask, 19, 75, 75)

        kernel = np.ones((5, 5), np.float32) / 25
        # mask = cv2.filter2D(mask, -1, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS )
        # contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE  )

        objects_contours = prepareContoursByAreaLen(contours, minArea, maxArea)

        return objects_contours
    def prepareContoursByAreaLen(contours, minArea, maxArea):
        objects_contours = []
        for cnt in contours:
            areaLen = cv2.arcLength(cnt, False)
            area = cv2.contourArea(cnt)
            # if cnt.size <= 4:
            #     continue
            # if area > minArea and area < maxArea:
            # if area > minArea and area < maxArea:
            if areaLen > 1000:
                extCtr = (cnt,areaLen)
                objects_contours.append(extCtr)
        # objtours = sorted(objects_contours, key=cv2.contourArea)[-1]
        objects_contours.sort(key=custom_key, reverse=True)
        return objects_contours

    def doContours(imgGray, img):
        # -------------------------------------
        # нахождение круговых вырезов
        circles = cvUtils.findCircles(imgGray, img, True)
        # -------------------------------------
        # фильтр изображения
        throu = 20
        cThr=[throu,throu]
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
        kernel = np.ones((5,5))
        imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
        imgThre = cv2.erode(imgDial,kernel,iterations=3)
        # imgCanny = imgGray
        imgTst = imgCanny
        # imgTst = imgGray
        # -------------------------------------
        # поиск главного контура
        # contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        # contours,hiearchy = cv2.findContours(imgTst,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours,hiearchy = cv2.findContours(imgTst,cv2.RETR_LIST ,cv2.CHAIN_APPROX_SIMPLE)
        # сортировка котуров по площади (максимальный первый)
        minArea=1000  
        sel_countour=None
        finalCountours = []
        for iCon in contours:
            area = cv2.contourArea(iCon)
            if area > minArea:
                peri = cv2.arcLength(iCon,True)
                approx = cv2.approxPolyDP(iCon,0.02*peri,True)
                bbox = cv2.boundingRect(approx)
                finalCountours.append([len(approx),area,approx,bbox,iCon])
        finalCountours = sorted(finalCountours,key = lambda x:x[1] ,reverse= True)                
        cvUtils.extractContours(finalCountours)
        
        # sel_countour = finalCountours[7][4]
        sel_countour = finalCountours[0][4]
        lines = cvUtils.drawContureLines(img, finalCountours[0][4],(255,0,0),5, 100)
        mainRect  =cvDraw.calkSize(sel_countour)
        cvUtils.createMainContours(lines, mainRect, circles, img)

        sel_countour = finalCountours[4][4]
        # lines = cvUtils.drawContureLines(img, finalCountours[4][4],(255,0,0),50, 100)
        # lines = cvUtils.drawContureLines(img, finalCountours[9][4],(255,0,0),50, 100)
        # lines = cvUtils.drawContureLines(img, finalCountours[10][4],(0,255,0),50, 100)
        # cvUtils.createMainContours(lines, mainRect, circles, img)
        
        return imgTst
    # border граница длин линий
    def drawContureLines(img, sel_countour, color, thickness=12, border=100):
        cv2.drawContours(image=img, contours=sel_countour, contourIdx=-1, color=color, thickness=thickness, lineType=cv2.LINE_AA)
        # return None
        
        lines = []
        last_point = None
        for point in sel_countour:
            curr_point=point[0]

            if not(last_point is None):
                line =cvDraw.packLine(last_point,curr_point, border)
                if line is not None:
                    lines.append(line)
            last_point=curr_point
        line =cvDraw.packLine(last_point,sel_countour[0][0], border)
        if line is not None:
            lines.insert(0,line)
        lines = lines[::-1]
        # lines = lines[1:5]

        for line in lines:
            cv2.line(img, line[0], line[1], color=(0,0,255), thickness=thickness)
        return lines
    def extractContours(finalCountours):
        result =[]
        for index in range(len(finalCountours)-1):
            counter = finalCountours[index]
            if index == 0:
                result.append(counter)  
                continue
            testedCounter = finalCountours[index-1]
            # testedCounter = result[::-1]
            ok = cvUtils.compareContours(counter, testedCounter)
            if ok == False:
              result.append(counter)  
        return result
    def compareContours(countourA, countourB):
        areaA = countourA[1]
        areaB = countourB[1]
        delta = abs(areaA- areaB)
        coff = delta / areaA
        if coff > 1:
            return False
        M = cv2.moments(countourA[4])
        cAX = int(M["m10"] / M["m00"])
        cAY = int(M["m01"] / M["m00"])
        M = cv2.moments(countourA[4])
        cBX = int(M["m10"] / M["m00"])
        cBY = int(M["m01"] / M["m00"])
        border = 10
        len = math.sqrt( ((cAX - cBX)**2)+(cAY - cBY)**2)
        if len > border:
            return False
        
        return True
    
    def getMainContours(imgGray, img, cThr=[100,100],showCanny=False,minArea=0,filter=0,draw =True):
        circles = cvUtils.findCircles(imgGray, img, True)
        
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
        kernel = np.ones((5,5))
        imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
        imgThre = cv2.erode(imgDial,kernel,iterations=3)
        # imgCanny = imgGray
        imgTst = imgCanny
        contours,hiearchy = cv2.findContours(imgTst,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        finalCountours = []
        for i in contours:
            area = cv2.contourArea(i)
            if area > minArea:
                peri = cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,0.02*peri,True)
                bbox = cv2.boundingRect(approx)
                finalCountours.append([len(approx),area,approx,bbox,i])
                
        max=0                
        sel_countour=None
        for countour in contours:
            if countour.shape[0]>max:
                sel_countour=countour
                max=countour.shape[0]
                
        mainRect  =cvDraw.calkSize(sel_countour)
        # получение линий
        lines = []
        last_point = None
        for point in sel_countour:
            curr_point=point[0]

            if not(last_point is None):
                line =cvDraw.packLine(last_point,curr_point, 100)
                if line is not None:
                    lines.append(line)
            last_point=curr_point
        line =cvDraw.packLine(last_point,sel_countour[0][0], 100)
        if line is not None:
            lines.insert(0,line)
        lines = lines[::-1]
        cvUtils.createMainContours(lines, mainRect, circles, img)

        for line in lines:
            cv2.line(img, line[0], line[1], (255,0,0), thickness=12)
        
        # if draw:
        for con in finalCountours:
            approx = cv2.approxPolyDP(con[4],0.2,True)
            # cv2.drawContours(img,con[4],-1,(255,0,0),16)
            # cv2.drawContours(img,[approx],-1,(0,255,0),6)
            # cv2.drawContours(img,con[4],-1,(0,255,0),16)
                
        # img = cv2.imdecode(np.fromfile("example.png", dtype=np.uint8), cv2.IMREAD_COLOR)

        return imgTst, finalCountours
    
    def createMainContours(lines, mainRect, circles, img):
        shape = img.shape
        width = int((mainRect[1][0]-mainRect[0][0]) * 1.5)
        height = int((mainRect[1][1]-mainRect[0][1]) * 1.5)
        width = shape[1]
        height = shape[0]
        d = drawSvg.Drawing(width, height, origin=(0,0), id_prefix='d11')
        # d = drawSvg.Drawing(8.2, 11.6, origin=(10,10), id_prefix='d11')
        p = drawSvg.Path(stroke='red', stroke_width=2, fill='none') 
        
        # добавление главного контура
        cvDraw.createConture(lines, d, p, 1)

        # добавление кругов
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = Point(i[0], i[1])
                radius = i[2]
                cvDraw.createCircle(d, int(radius), int(center.x), int(center.y),1)
        
        d.save_svg('example.svg')     
        
        # dwg = svgwrite.Drawing('test.svg', profile='tiny')
        # dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
        # dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))
        # dwg.save()
        
        # dwg = svgwrite.Drawing('myDrawing.svg', size=('170in', '130in'), viewBox=('0 0 170 130'))
        # dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
        # dwg.save()        
        # dwg.im.Image('myDrawing.png')
        return
        # d.save_png('example.png')
        