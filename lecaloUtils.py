import cv2
import numpy as np
import lekaloFilter
from PIL import Image
import pillow_heif
import os
import lekaloDraw

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
    lekaloDraw.drawContures(objects_contours, aligmentedImgColor, 4)
    cv2.imwrite('and.png',aligmentedImgColor)

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

def findCircles(img):
    circles = cv2.HoughCircles(img,
                               cv2.HOUGH_GRADIENT_ALT,
                               dp=32,  # resolution of accumulator array.
                               # dp=rows/8,  # resolution of accumulator array.
                               minDist=1,  # number of pixels center of circles should be from each other, hardcode
                               param1=50,
                               param2=70,

                               # param1=50,
                               # param2=100,
                               # param1=150,
                               # param2=50,

                               minRadius=5,  # HoughCircles will look for circles at minimum this size
                               maxRadius=20  # HoughCircles will look for circles at maximum this size
                               )
    return circles

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

def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho

def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y

def rotate_contour(cnt, angle):
    M = cv2.moments(cnt)
    if M['m00'] == 0:
        return cnt
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    cnt_norm = cnt - [cx, cy]

    coordinates = cnt_norm[:, 0, :]
    xs, ys = coordinates[:, 0], coordinates[:, 1]
    thetas, rhos = cart2pol(xs, ys)

    thetas = np.rad2deg(thetas)
    thetas = (thetas + angle) % 360
    thetas = np.deg2rad(thetas)

    xs, ys = pol2cart(thetas, rhos)

    cnt_norm[:, 0, 0] = xs
    cnt_norm[:, 0, 1] = ys

    cnt_rotated = cnt_norm + [cx, cy]
    cnt_rotated = cnt_rotated.astype(np.int32)

    return cnt_rotated

def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    if M['m00'] == 0:
        return cnt
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled

def move_contour(cnt, dispX, dispY):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_moved = cnt_norm + [cx + dispX, cy + dispY]
    cnt_moved = cnt_moved.astype(np.int32)

    return cnt_moved

def findArucoMarkers(img, markerSize = 6, totalMarkers=250, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(cv2.aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = cv2.aruco.Dictionary_get(key)
    arucoParam = cv2.aruco.DetectorParameters_create()
    bboxs, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    if draw:
        cv2.aruco.drawDetectedMarkers(img, bboxs)
    return [bboxs, ids]

def arucoAug(bbox, img, imgAug):
    tl = bbox[0][0][0], bbox[0][0][1]
    tr = bbox[0][1][0], bbox[0][1][1]
    br = bbox[0][2][0], bbox[0][2][1]
    bl = bbox[0][3][0], bbox[0][3][1]
    h, w, c = imgAug.shape
    pts1 = np.array([tl, tr, br, bl])
    pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
    matrix, _ = cv2.findHomography(pts2, pts1)
    imgout = cv2.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
    return imgout

def readImageFile(name):
    filename, file_extension = os.path.splitext(name)
    if file_extension.lower() == '.heic':
        heif_file = pillow_heif.read_heif(name)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        img = np.array(image)
        # img = cv2.resize(img, (0, 0), cv2.INTER_LANCZOS4, 0.5, 0.5)
        return img
    img = cv2.imread(name);
    return img

def convertHEICtoJPG(name):
    filename, file_extension = os.path.splitext(name)
    if file_extension.lower() == '.heic':
        img = readImageFile(name)
        nameJpg = filename + '.jpg'
        cv2.imwrite(nameJpg, img);
        return nameJpg
    return None