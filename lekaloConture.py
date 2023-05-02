import math
import os
import glob

import cv2

import lecaloUtils
import lekaloFilter
import lekaloDraw
import numpy as np
import arucoSize
from numpy import unravel_index

def doScanContures(aligmentedImgGray):
    files = glob.glob('./temp/*')
    for f in files:
        os.remove(f)

    for paramA in range(3, 40, 2):
        for paramB in range(11, 30):
            img = doPrepareFrameV_GetMainContur(aligmentedImgGray, paramA, paramB);
            img = doPrepareFrameV_1(img, 200, 1, 0.2, 8)
            # Детектирование контура телефона
            # contours, imgUpd, circles = lecaloUtils.detect_objects(img, 200, 1)
            contours, imgUpd, circles = lecaloUtils.detect_contures(img)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            img[:] = (255, 255, 255)
            for cnt in contours:
                cv2.polylines(img, [cnt], True, (0, 255, 0), 2)

            name = './temp/'+'zzz'+str(paramA) + '_' + str(paramB) + '.jpg'
            res = cv2.imwrite(name, img)
            continue
    return

def doPrepareFrameV_1(aligmentedImgGray, current_value1, current_value2, clipLimit,tileGridSize):
    # Create a Mask with adaptive threshold
    # imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # imgBlur = cv2.medianBlur(gray, 5)
    # imgBlur = cv2.GaussianBlur(frame,(5,5),1)
    imgBlur = cv2.GaussianBlur(aligmentedImgGray,(5,5), 1)
    imgCanny = cv2.Canny(imgBlur,current_value1, current_value1+5)
    # imgCanny = cv2.Canny(imgBlur,100, 200)
    kernel = np.ones((5,5),np.uint8)
    imgDial = cv2.dilate(imgCanny,kernel,iterations=13)
    imgThre = cv2.erode(imgDial,kernel,iterations=13)

    mask = imgCanny
    return mask

def doPrepareFrameV_GetMainContur(aligmentedImgGray, paramA=19, paramB=11):
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 11)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 11)
    mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, paramA, paramB)
    return mask

def pRectToBox(phoneRect):
    box = cv2.boxPoints(phoneRect) # поиск четырех вершин прямоугольника
    box = np.int0(box) # округление координат
    return box

def preparePhoneRect(phoneRect):
    box = cv2.boxPoints(phoneRect) # поиск четырех вершин прямоугольника
    box = np.int0(box) # округление координат
    # нахождение верхних точек
    (x, y), (w, h), angle = phoneRect
    phoneAngle = findTop(box)
    phoneAngle = -1
    if phoneAngle >0:
        angle = 90 - angle + 180
    else:
        angle = -angle
    if w < h:
        angle = angle + 90

    return angle

def findTop(box):
    maxT = 0
    minB = 100000
    indexT =-1
    indexB =-1
    for index in  range(0, 4):
        point = box[index]
        y = point[1]
        if y>maxT:
            maxT =y
            indexT = index
        if y < minB:
            minB = y
            indexB = index
    if indexT >= 0 and indexB >= 0:
        pointTx = box[indexT][0]
        pointBx = box[indexB][0]
        if pointTx > pointBx:
            return 1
    return -1

# обработка и вырезание телефона из выровненой картинки
def processBorderPhone(x, y, w, h, imgRotated, params, pixel_cm_ratio, paramBorder):
    x1 = x - (w/2)
    y1 = y - (h/2)

    x = arucoSize.myRound(x1)
    y = arucoSize.myRound(y1)
    w = arucoSize.myRound(w)
    h = arucoSize.myRound(h)

    # результирующа картинка
    imgResult1  = imgRotated[y:y + h, x:x + w]
    # imgResult1 = np.flip(imgResult1, axis=0)
    imgRotated = imgResult1.copy()
    # --------------------------------------------------------------------
    # получение краев
    wRotated = imgRotated.shape[1]
    hRotated = imgRotated.shape[0]

    # анализ кнопок в прделах 1/10 размера телефона
    border = (int)(wRotated / 8)
    imgRotatedL  = imgRotated[0:hRotated, 0:border]
    imgRotatedR  = imgRotated[0:hRotated, wRotated-border:wRotated]

    gray = cv2.cvtColor(imgRotated, cv2.COLOR_RGB2GRAY)
    # resultH, resultW,_ = imgResult.shape
    resultH, resultW,_ = imgRotated.shape

    # анализ границ в прделах 1/20 размера телефона
    scanSizeW = (int)(resultW / 20)
    scanSizeH = (int)(resultH / 20)

    # нахождение грпниц по горизоньали
    lb, rb=findBound(gray, 0, scanSizeW)
    # нахождение грпниц по вертикали
    lv, rv=findBound(gray, 1, scanSizeH)

    # верезание кртинки по границе
    imgResult = imgRotated[lv:rv, lb:rb]

    cv2.imwrite('res.jpg',imgResult)
    round0 = findRound(imgResult,0)
    round1 = findRound(imgResult,1)
    round = max(round0, round1)
    # добавление границ
    addedW, addedH = params
    addedW = (int)(addedW * pixel_cm_ratio * 0.1)
    addedH = (int)(addedH * pixel_cm_ratio * 0.1)

    leftPhone = lb + addedW
    rightPhone = rb - addedW
    cntPhone = (leftPhone, rightPhone, lv+addedH, rv-addedH, x, y, round)

    # создание нижней и верхней части телефона
    # нижняя часть телефона
    cntTop = createPhoneTopAndBottomContures('afterL.png', 'afterLA.png', imgRotatedL, paramBorder,  False, 0, pixel_cm_ratio,cntPhone)
    # верхняя часть телефона
    cntBottom = createPhoneTopAndBottomContures('afterR.png', 'afterRA.png', imgRotatedR, paramBorder,True, wRotated - border, pixel_cm_ratio,cntPhone)
    cnt = cntTop + cntBottom

    return imgResult, cntPhone, cnt
    # return imgResult, (lb+addedW, rb-addedW, lv+addedH, rv-addedH, x, y, round), cnt

# нахождение отверстий в корпусе телефона
def findHoles():
    testImage = cv2.imread('afterRA.png')
    testImage = cv2.cvtColor(testImage, cv2.COLOR_RGB2GRAY)
    circles = lecaloUtils.findCircles(testImage)
    # lecaloUtils.drawCircles(testImage, circles)
    contours, imgUpd, circles = lecaloUtils.detect_contures(testImage, 1, 2000)
    testImage = cv2.cvtColor(testImage, cv2.COLOR_GRAY2RGB)
    for cnt in contours:
        # continue
        cv2.polylines(testImage, [cnt[0]], True, (0, 255, 0), 2)

    # cv2.polylines(testImage, [contours], True, (0, 0, 255), 2)
    cv2.imwrite('afterLA.png',testImage)
    return
# нохождение границ корпуса
def findBound(img, axis, lenBound):
    # вырезаем массив с границами
    h,w, = img.shape[:2]
    if axis==0:
        sizeAxis = h
        scan = (int)(sizeAxis / 10)
        stScan = scan
        lenScan = sizeAxis - scan
        tstImg = img[stScan:lenScan, 0:w]
    else:
        sizeAxis = w
        scan = (int)(sizeAxis / 10)
        stScan = scan
        lenScan = sizeAxis - scan
        tstImg = img[0:h, stScan:lenScan]

    # получаем среднее значение по каждому столбцу
    tstArr = np.sum(tstImg, axis = axis)
    tstArr = (tstArr/sizeAxis)
    tstArr = tstArr.astype(int)

    coffL = 1.2
    coffR = 1.5
    # coffL = coffR =1
    averL = np.sum(tstArr[0:lenBound]) / lenBound
    lvL = np.where(tstArr[0:lenBound] < averL * coffL)
    lb = lvL[0][0]

    if axis==0:
        averR = np.sum(tstArr[w-lenBound:w]) / lenBound
        lvR = np.where(tstArr[w-lenBound:w] > averR * coffR)
        if len(lvR[0])== 0:
            rb = w
        else:
            rb = w-lenBound + lvR[0][0]
    else:
        averR = np.sum(tstArr[h - lenBound:h]) / lenBound
        lvR = np.where(tstArr[h - lenBound:h] > averR * coffR)
        if len(lvR[0])== 0:
            rb = h
        else:
            rb = h - lenBound + lvR[0][0]
    return lb, rb
# нохождение скругления корпуса
def findRound(img, mode):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h,w, = gray.shape
    param = []

    # анализ закругления телефона  в прделах 1/20 размера телефона
    sizeRoundRect = (int)(w/20)

    if mode == 0:
        imgCorner = gray[0:sizeRoundRect, 0:sizeRoundRect]
        corner = np.diagonal(imgCorner)
    if mode == 1:
        imgCorner = gray[0:sizeRoundRect, w-sizeRoundRect:w]
        imgCorner = np.fliplr(imgCorner)
        corner = np.diagonal(imgCorner)

    delta = []
    if len(corner) <= 2:
        return 0
    for index in range (1, len(corner) -1):
        val = abs(int(corner[index])-int(corner[index+1]))
        if val> 10:
            return index
        delta.append(val)
    round = np.argmax(delta)
    return round

#  dispFromBottom отступ в пикселях от нижнего края телефона
def createPhoneTopAndBottomContures(nameSrc, nameDst, img, paramBorder, isTop, dispFromBottom, pixel_cm_ratio, cntPhone):
    if(img is None) == True:
        return
    cv2.imwrite(nameSrc, img)
    imgResult = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # imgResult = lekaloFilter.cannyContur(imgResult, paramBorder)
    imgResult = lekaloFilter.cannyContur(imgResult, 27)

    '''    
    imgResult = lekaloFilter.cannyContur(imgResult, 20)
    imgResult = lekaloFilter.adaptiveTresholdContur(imgResult, paramBorder)
    # imgResult = lekaloFilter.cannyContur(imgResult, 35)

    # imgResult = lekaloFilter.cannyContur(aligmentedImgGray, current_value1)
    '''
    contours, imgUpd, lines, _ = lecaloUtils.detect_contures(imgResult, 10, 2000)

    imgResult = cv2.cvtColor(imgResult, cv2.COLOR_GRAY2RGB)
    lekaloDraw.drawContures(contours,imgResult)
    # определение кнопок и дырок
    cntOut = findObectsInPhone(contours, imgResult, isTop, dispFromBottom, pixel_cm_ratio,cntPhone)

    # cv2.drawContours(imgResult, contours1], 0, (0, 0, 255), 2)
    # drawContures(contours1, imgRotatedL)
    # lines = sorted(lines, key=cv2.contourArea)[-1]

    # lekaloDraw.drawLines(lines, imgResult, minShowsize=100)
    cv2.imwrite(nameDst, imgResult)
    return cntOut
def findObectsInPhone(contours, img, isTop, dispFromBottom, pixel_cm_ratio,cntPhone):
    cntOut = []
    pixel_mm_ratio = pixel_cm_ratio/10
    # добавление размера дыркам (mm)
    addedCorner = 0.25 * pixel_mm_ratio
    height = img.shape[0]
    width = img.shape[1]
    for cntExt in contours:
        cnt = cntExt[0]
        area = cv2.contourArea(cnt)
        if area < 5 or area > 2000:
            continue

        rect = cv2.minAreaRect(cnt)
        (x, y), (w, h), angle = rect

        circle = isCircle(cnt, dispFromBottom,addedCorner)
        if (circle is None) == False:
            # lekaloDraw.drawCircles(circle, img)
            _,param = circle
            x,y,radius,_ = param
            # дырка не должна выходить за грань корпуса
            # внизу
            if isTop == False:
                centerX = width / 2
                maxDisp = centerX / 5
                if x > centerX + maxDisp or x < centerX - maxDisp:
                    continue

            # отсекаем крйние круги
            centerH = height / 2
            border = height / 8
            # centerH = y + (height / 2)
            if y < border or y > height - border:
                continue

            cv2.circle(img, ((int)(x), (int)(y)), (int)(radius), (255, 0, 255), 2)
            cntOut.append(circle)
            continue

        areaRect = w * h
        if areaRect  > 2000:
            continue
        if areaRect  < 500:
            continue
        if isTop == False:
            continue
        # отсекаем крйние прамоугольники по высоте
        border = height / 4
        yCenterRect = y + (w / 2)
        if  yCenterRect<border or yCenterRect> height - border:
            continue
        # на правой грани прямоугольники не рисуются (1/8 ширины)
        borderW = width / 8
        if x > width - borderW:
            continue

        # Display rectangle
        box = cv2.boxPoints(rect)
        box = createBox(box, dispFromBottom,0)
        # box = createBox(box, dispFromBottom,addedCorner)
        cv2.rectangle(img, box[0], box[1], (0, 255, 0), 3)

        cntOut.append(['b', box])
    cntOut = deleteNested(cntOut)
    if len(cntOut)> 5:
        return []
    return cntOut

def getCirleParam(param):
    type = param[0]
    param = param[1]
    if type == 'c':
        x = param[0]
        y = param[1]
        r = param[2]
        return (x,y,r)
    return None

# проверка входит ли круг в другой круг
def deleteNested(cntIn):
    cntOut =[]
    for cnt in cntIn:
        doAdd = True
        param =  getCirleParam(cnt)
        if (param is None)==False:
            radius = param[2]
            for cntTest in cntIn:
                if (cntTest is cnt) == False:
                    paramTest= getCirleParam(cntTest)
                    if (paramTest is None) == False:
                        radiusTest = paramTest[2]
                        if radius < radiusTest:
                            point_1 = np.array((paramTest[0], paramTest[1]))
                            point_2 = np.array((param[0], param[1]))
                            square = np.square(point_1 - point_2)
                            sum_square = np.sum(square)
                            distance = np.sqrt(sum_square)
                            if radius > distance:
                                doAdd = False

        if doAdd == True:
            cntOut.append((cnt))
    return cntOut
def createBox(box, dispFromBottom,addedCorner):
    box = np.int0(box)
    minX = 10000
    maxX = 0
    minY = 10000
    maxY = 0
    for point in box:
        x = point[0]
        y = point[1]
        maxX = max(x, maxX)
        minX = min(x, minX)
        maxY = max(y, maxY)
        minY = min(y, minY)
        continue
    box = ((int(minX-addedCorner),int(minY-addedCorner)),(int(maxX+addedCorner),int(maxY+addedCorner)),0.1, dispFromBottom)
    # box = ((minX,minY),(maxX,maxY),0.1, dispFromBottom)
    # box = ((minY,minX),(maxY,maxX),0.2)
    return box

def isCircle(cnt, dispFromBottom,addedCorner):
    rect = cv2.minAreaRect(cnt)
    (x, y), (w, h), angle = rect
    prop = w / h
    delta = 0.5
    if prop > 1 - delta and prop < 1 + delta:
        (x1, y1), radius = cv2.minEnclosingCircle(cnt)
        return ['c', (x1, y1, radius + addedCorner, dispFromBottom)]
    return None

def isInRange(testVal, baseVal, scaleVal, isIn):
    center = baseVal / 2
    thres = center * scaleVal
    if testVal > center - thres and testVal < center + thres and isIn == True:
        return True
    if (testVal < center - thres or testVal > center + thres) and isIn == False:
        return True
    return False
