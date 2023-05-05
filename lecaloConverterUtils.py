import cv2
import numpy as np

class cvUtils:
    def findCircles(img_grey, img_Draw, draw_conrure):
        rows = img_grey.shape[0]
        circles = cv2.HoughCircles(img_grey, cv2.HOUGH_GRADIENT, 1, rows / 64,
                                param1=100, param2=30,
                                minRadius=10, maxRadius=1000)            
        if draw_conrure == True:
            if circles is not None :
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    center = (i[0], i[1])
                    # circle center
                    cv2.circle(img_Draw, center, 1, (0, 100, 100), 3)
                    # circle outline
                    radius = i[2]
                    cv2.circle(img_Draw, center, radius, (255, 0, 255), 8)
        return

def getContours(img,cThr=[100,100],showCanny=False,minArea=1000,filter=0,draw =False):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
    kernel = np.ones((5,5))
    imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
    imgThre = cv2.erode(imgDial,kernel,iterations=3)
    if showCanny:cv2.imshow('Canny',imgCanny)
    # contours,hiearchy = cv2.findContours(imgThre,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
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
    finalCountours = sorted(finalCountours,key = lambda x:x[1] ,reverse= True)
    if draw:
        for con in finalCountours:
            cv2.drawContours(img,con[4],-1,(0,0,255),3)
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

def findLines(img):
    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 40  # maximum gap in pixels between connectable line segments

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]),min_line_length, max_line_gap)
    return lines

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
