import math
import cv2
import lekaloConture
import lecaloUtils
import lekaloDraw
import numpy as np
import arucoSize
import lekaloSvg
import lekaloFilter

def saveToSvg(img, nameSvg):
    findCtr, imgUpd, cnt, imgConture, imgFiltered ,_ ,_ = doFrame(img, False, 200, 1, 0.2, 8)
    if findCtr == True:
        lekaloSvg.conturToSvg(cnt, nameSvg)

def doFrame(img, current_value1, current_value2, clipLimit, tileGridSize, params):
    # анализ положения маркеров
    aligmentedImg, markers, markerIds = arucoSize.arucoWarp(img)

    # если markers строка то маркеры не обнаружены ()
    if isinstance(markers, str):
        # контура нет , текст. данных о контуре нет
        return False, markers, None, None, None, None, None

    arucoSize.arucoGetSize(aligmentedImg,markers, markerIds)
    img = cv2.aruco.drawDetectedMarkers(img, markers, markerIds, (200, 0, 0))
    aligmentedImg = np.flip(aligmentedImg, axis=0)

    # выровненое  и обрезанное по маркерам изображение
    aligmentedImgGray = cv2.cvtColor(aligmentedImg, cv2.COLOR_RGB2GRAY)
    # lekaloConture.doScanContures(aligmentedImgGray)
    width, height = aligmentedImg.shape[:2]
    # минимальна площадь телефона (в десять раз меньше маркировачной площади)
    squareViewMin = height * width  / 10
    mainConture, mainImgConture  = lecaloUtils.detect_main_conture(aligmentedImgGray, squareViewMin)
    # mainConture = None

    if (mainConture is None) == True:
        cv2.imwrite('bad.png', img)
        # return False, 'Телефон не найден', None, aligmentedImg, aligmentedImgGray1, aligmentedImgGray2
        return False, aligmentedImg, None, aligmentedImg, aligmentedImgGray, aligmentedImgGray, mainImgConture

    # --------------------------------------------------------------------
    # 1 . нахождение главны контур
    arucoSize.viewDirection(aligmentedImg, markers, markerIds)
    # ширина между маркерами на реальном обьекте
    distMarkers = 10.0
    heightReal = height * distMarkers
    pixel_cm_ratio = width / distMarkers
    # в одном мм столько пикселей
    mm_pix = width/ (distMarkers * 10)
    rect = cv2.minAreaRect(mainConture)
    (x, y), (w, h), angle = rect
    # 2 . получение реального прямоугольника где расположен телефон
    angle = lekaloConture.preparePhoneRect(rect)
    if w < h:
        w, h = h, w
    center = (x,y)
    # --------------------------------------------------------------------
    # получение повернутой коартинки для маска
    # 3 . поворот картинки на полученнй угол
    # aligmentedImg = np.flip(aligmentedImg, axis=0)
    imgResult = aligmentedImg.copy()

    imgRotatedBase = lekaloFilter.rotateImage(imgResult, -angle, center, scale=1.0)
    # imgRotatedBase = np.flip(imgRotatedBase, axis=0)

    # 4 . точное выделениние корпуса телефона (conturePhone)
    #     вырезание результирующей картинки
    imgFinal, conturePhone, contureHoles =lekaloConture.processBorderPhone(x, y, w, h, imgRotatedBase, params, pixel_cm_ratio, current_value2/2)
    resultH = conturePhone[3]-conturePhone[2]
    resultW = conturePhone[1]-conturePhone[0]
    # resultH, resultW,_ = imgFinal.shape
    object_width = resultW / pixel_cm_ratio
    object_height = resultH / pixel_cm_ratio

    # отображение найденных контуров (главный + дырки)
    lekaloDraw.drawConturePhone(conturePhone, imgRotatedBase, object_width, object_height, 1)
    lekaloDraw.drawFinalContures(conturePhone, contureHoles, imgRotatedBase, 3)

    # lekaloConture.drawHolesInPhone(contureHoles, imgRotatedBase)

    cv2.imwrite('imgRotatedBase.png', imgRotatedBase)
    cv2.imwrite('imgFinal.png', imgFinal)
    # отобразить параметры выделения телефона
    imgResult = imgFinal

    resultImgGray = cv2.cvtColor(imgResult, cv2.COLOR_RGB2GRAY)
    resultImgGray = lekaloFilter.adaptiveTresholdContur(resultImgGray, current_value2/2)
    # resultImgGray = doPrepareFrameV_1(resultImgGray, 200, 1, 0.2, 8)
    imgResult = cv2.cvtColor(resultImgGray, cv2.COLOR_GRAY2RGB)

    # --------------------------------------------------------------------
    # Детектирование контура телефона
    imgConture = aligmentedImg.copy()
    imgConture[:] = (128, 128, 128)
    imgRotatedResult = imgFinal.copy()

    contours, imgUpd, circles,_ = lecaloUtils.detect_contures(resultImgGray, 10, 200000)
    # mainConturePhone = findMainContures(contours, imgRotatedResult, conturePhone)
    # lekaloConture.drawContures(contours, imgRotatedResult)

    cv2.putText(imgRotatedResult, "angle {}".format(round(angle, 1)), (80, 165), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    resultCnt = createContures(conturePhone, contureHoles, pixel_cm_ratio)

    #                                       1                2                3               0
    return True, aligmentedImg, resultCnt, resultImgGray,  imgRotatedBase, imgRotatedResult, mainImgConture

def isInRange(testVal, baseVal, scaleVal, isIn):
    center = baseVal / 2
    thres = center * scaleVal
    if testVal > center - thres and testVal < center + thres and isIn == True:
        return True
    if (testVal < center - thres or testVal > center + thres) and isIn == False:
        return True
    return False

# s размеры главного контура
# s главный контур
# c круг
# b прямоугольник
# отступ по главному контуру (mm)
def createContures(conturePhone, contureHoles, pixel_cm_ratio):
    cntOut = []
    cntOut.append(['s', (conturePhone[1]-conturePhone[0]), (conturePhone[3]-conturePhone[2]), pixel_cm_ratio, conturePhone[4], conturePhone[5], conturePhone[6]])
    cntOut.append(['m', conturePhone])
    for cnt in contureHoles:
        type = cnt[0]
        fig = cnt[1]
        cntOut.append(cnt)
        continue
    return cntOut

