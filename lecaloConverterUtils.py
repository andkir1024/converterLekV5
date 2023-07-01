import copy
import cv2
import numpy as np
import math
from classifier import classifier
from cornerFig import LineStatus, CircuitSvg
from drawUtils import cvDraw
import drawsvg as drawSvg
from shapely import Point
import pathlib
import os


class cvUtils:
    # базовые константы для анализа
    # минимальная длина линии для выделения непрерывных линий
    MIN_LEN_LINE = 100
    # минимальная длина линии для работы в изогнутых фигурах
    MIN_LEN_CURVE_LINE = 10

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
        lines = cv2.HoughLinesP(
            img_grey,
            rho=1,
            theta=np.pi / 180,
            threshold=5,
            minLineLength=500,
            maxLineGap=40,
        )

        # lines = cv2.HoughLines(img_grey, rho = 1, theta = 1 * np.pi/180, threshold=120, srn=0, stn = 0, min_theta=1, max_theta=2)

        for i in range(0, len(lines)):
            rho, theta = lines[i][0][0], lines[i][0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(img_Draw, (x1, y1), (x2, y2), (0, 0, 255), 2)

    def findCircles(img_grey, img_Draw, draw_conrure):
        rows = img_grey.shape[0]
        circles = cv2.HoughCircles(
            img_grey,
            cv2.HOUGH_GRADIENT,
            1,
            rows / (64),
            param1=160,
            param2=80,
            # param1=160, param2=110,
            # param1=40, param2=40,
            # param1=200, param2=10,
            # param1=100, param2=30,
            minRadius=3,
            maxRadius=1000,
        )
        if draw_conrure == True:
            if circles is not None:
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
        ver = (cv2.__version__).split(".")
        if int(ver[0]) < 3:
            detector = cv2.SimpleBlobDetector(params)
        else:
            detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs.
        keypoints = detector.detect(img_Draw)

        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
        # the size of the circle corresponds to the size of blob

        img_Draw = cv2.drawKeypoints(
            img_Draw,
            keypoints,
            np.array([]),
            (0, 0, 255),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )

        return

    def reorder(myPoints):
        # print(myPoints.shape)
        myPointsNew = np.zeros_like(myPoints)
        myPoints = myPoints.reshape((4, 2))
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] = myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew

    def findDis(pts1, pts2):
        return ((pts2[0] - pts1[0]) ** 2 + (pts2[1] - pts1[1]) ** 2) ** 0.5

    def custom_key(extCtr):
        return extCtr[1]

    def doContours(imgGray, img, filesSrc, svgDir, dpiSvg,pngDir):
        # -------------------------------------
        # нахождение круговых вырезов
        circles = cvUtils.findCircles(imgGray, img, True)
        # -------------------------------------
        # фильтр изображения
        throu = 20
        cThr = [throu, throu]
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        imgCanny = cv2.Canny(imgBlur, cThr[0], cThr[1])
        kernel = np.ones((5, 5))
        imgDial = cv2.dilate(imgCanny, kernel, iterations=3)
        imgThre = cv2.erode(imgDial, kernel, iterations=3)
        # imgCanny = imgGray
        imgTst = imgCanny
        # imgTst = imgGray
        # -------------------------------------
        # поиск главного контура
        # contours,hiearchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        # contours,hiearchy = cv2.findContours(imgTst,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        contours, hiearchy = cv2.findContours(
            imgTst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        # contours,hiearchy = cv2.findContours(imgTst,cv2.RETR_CCOMP  ,cv2.CHAIN_APPROX_SIMPLE)
        # сортировка котуров по площади (максимальный первый)
        minArea = 1000
        # sel_countour=None
        finalCountours = []
        for iCon in contours:
            area = cv2.contourArea(iCon)
            if area > minArea:
                peri = cv2.arcLength(iCon, True)
                approx = cv2.approxPolyDP(iCon, 0.02 * peri, True)
                bbox = cv2.boundingRect(approx)
                finalCountours.append([0, area, approx, bbox, iCon, None])
        finalCountours = sorted(finalCountours, key=lambda x: x[1], reverse=True)
        # finalCountoursA = []
        # finalCountoursA.append(finalCountours[1])
        # finalCountours = finalCountoursA
        finalCountours = cvUtils.extractContours(finalCountours, circles)

        # генерация параметров контуров
        for countour in finalCountours:
            lines = classifier.classifieCounter(
                countour[4], cvUtils.MIN_LEN_LINE, 0, -1
            )
            if lines is None:
                continue
            countour[5] = lines
            continue

        # отображенипе контуров (1 000 000)
        for countour in finalCountours:
            if img is not None:
                lines = countour[5]
                if lines is not None:
                    classifier.drawFigRect(img, countour, lines)

        cvUtils.createMainContoursSvg(
            finalCountours, circles, imgGray, filesSrc, svgDir, dpiSvg,pngDir
        )
        return imgTst

    # border граница длин линий
    def drawContureLines(img, sel_countour, color, thickness, border):
        lines = classifier.classifieCounter(sel_countour, cvUtils.MIN_LEN_LINE, 0, -1)
        if img is not None:
            classifier.drawFigRect(img, sel_countour, lines)
        return lines

    def MarkedAndAligmentLinesInConture(lines):
        if lines is None:
            return None
        linesDst = []
        linesDst.append(lines[0].copy())
        linesDst[-1] = cvUtils.swapPoint(linesDst[-1])
        for index in range(1, len(lines) - 0):
            # последняя точка текущей линии
            linesDst.append(lines[index].copy())

            pointAF = linesDst[-2][1]
            # start
            pointBS = linesDst[-1][0]
            # finish
            pointBF = linesDst[-1][1]

            distAFBS = cvDraw.distancePoint(pointAF, pointBS)
            distAFBF = cvDraw.distancePoint(pointAF, pointBF)
            if distAFBS > distAFBF:
                linesDst[-1] = cvUtils.swapPoint(linesDst[-1])
                linesDst[-1][5] = int(distAFBF)
            else:
                linesDst[-1][5] = int(distAFBS)

            continue
        # mark seq
        for index in range(0, len(linesDst) - 1):
            distance = linesDst[index + 1][5]
            if distance < 10 and index > 0:
                linesDst[index][2] = LineStatus.sequest
        # test
        for index in range(0, len(linesDst) - 1):
            pp0 = 0
            stat = linesDst[index][2]
            if stat != LineStatus.sequest:
                distAFBS = cvDraw.distancePoint(pointAF, pointBS)
                pp0, pp1, centroid1, centroid2, pp2 = cvDraw.createAngle(
                    linesDst[index][0],
                    linesDst[index][1],
                    linesDst[index + 1][0],
                    linesDst[index + 1][1],
                )
                if pp0 is None:
                    linesDst[index][2] = LineStatus.parallel

                # par = cvDraw.is_parallel(linesDst[index], linesDst[index+1])
                # if par == True and linesDst[index][3] < 40 :
                #     linesDst[index][2]=LineStatus.parallel

            continue
        # correction parallel
        for index in range(0, len(linesDst) - 1):
            stat = linesDst[index][2]
            if stat == LineStatus.parallel:
                zz = 1
                cvDraw.aligmentParallel(linesDst[index], linesDst[index + 1])

        # linesDst = linesDst[6:-1]
        # linesDst = linesDst[0:5]
        # linesDst = linesDst[0:len(linesDst)-1]
        # linesDst.insert(0,linesDst[-1])
        # del linesDst[-1]
        return linesDst

    def swapPoint(pointSrc):
        pointDst = pointSrc
        pointDst[0], pointDst[1] = pointDst[1], pointDst[0]
        return pointDst

    def extractContours(finalCountours, circles):
        result = []
        for index in range(len(finalCountours) - 1):
            counter = finalCountours[index]
            if index == 0:
                counter[0] = 1
                result.append(counter)
                continue
            ok = False
            for counterForTest in result:
                if cvUtils.compareContours(counter, counterForTest, circles) == True:
                    ok = True
            if ok == False:
                if counter[1] > 1000000:
                    counter[0] = 1
                result.append(counter)
        return result

    # True добавлять не надо
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

        isCircle = cvUtils.isContourCircle(cAX, cAY, circles)
        if isCircle == True:
            return True
        if coff > 1:
            return False
        if len > border:
            return False

        return True

    def calkCenter(countour):
        M = cv2.moments(countour[4])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return cX, cY

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

    def createMainContoursSvg(finalCountours, circles, img, filesSrc, svgDir, dpiSvg,pngDir):
        # return
        width = 4000
        height = 8000
        if img is not None:
            width = img.shape[1]
            height = img.shape[0]
        # создам svg для
        dPrn = cvUtils.createSvg(finalCountours, circles, width, height, True, dpiSvg,pngDir)
        svgTestName = "example.svg"
        dPrn.save_svg(svgTestName)
        pngTestName = "example.png"
        d = cvUtils.createSvg(finalCountours, circles, width, height, False, dpiSvg,pngDir)
        d.save_png(pngTestName)
        cvUtils.saveResult(img, filesSrc, svgDir, svgTestName, pngTestName,pngDir)
        return

    def createSvg(finalCountours, circles, width, height, printSvg, dpiSvg,pngDir):
        dpi = 1
        stroke_width = 10
        colorCircle = "blue"
        if printSvg == True:
            # dpi =6.8
            # dpi = dpi * 1.33
            dpi = dpiSvg
            stroke_width = 1
            colorCircle = "red"
        d = drawSvg.Drawing(width, height, origin=(0, 0))
        # d.set_pixel_scale(2)  # Set number of pixels per geometry unit
        # d.set_render_size(400, 200)  # Alternative to set_pixel_scale
        for countour in finalCountours:
            if countour[0] == 1:
                # главный контур
                p = drawSvg.Path(stroke="red", stroke_width=stroke_width, fill="none")
                lines = countour[5]
                if lines is not None:
                    circles = CircuitSvg.createContureSvg(lines, d, p, dpi, circles)
                continue
            else:
                # отверстия в лекале
                p = drawSvg.Path(stroke="red", stroke_width=stroke_width, fill="none")
                lines = countour[5]
                if lines is not None:
                    circles = CircuitSvg.createContureSvg(lines, d, p, dpi, circles)
                continue

        # добавление кругов
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = Point(i[0], i[1])
                radius = i[2]
                if radius != 0:
                    cvDraw.createCircle(
                        d,
                        int(radius),
                        int(center.x),
                        int(center.y),
                        dpi,
                        stroke_width,
                        colorCircle,
                    )
        return d

    # сохранение результатов
    def saveResult(img, filesSrc, svgDir, svgTestName, pngTestName,pngDir):
        if not os.path.isdir(svgDir):
            os.mkdir(svgDir)
        name = pathlib.Path(filesSrc).stem
        name =name.removesuffix('.prn')
        nameSvg = svgDir + "/" + name + ".svg"
        # nameSvg = "result.svg"
        with open(svgTestName, "r") as f1, open(nameSvg, "w") as f2:
            lines = f1.readlines()

            for line in lines:
                line = line.strip() + "\n"
                key = line.find("viewBox")
                if key >= 0:
                    f2.write(
                        'width="8.2677in" height="11.6929in" viewBox="0 0 595.2756 841.8898">\n'
                    )
                else:
                    f2.write(line)

        imgSvg = cv2.imread(pngTestName)
        imgSrc = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        alpha = 0.5
        out_img = np.zeros(imgSvg.shape, dtype=imgSvg.dtype)
        out_img[:, :, :] = (alpha * imgSvg[:, :, :]) + ((1 - alpha) * imgSrc[:, :, :])
        cv2.imwrite("out.png", out_img)
        sought = [0, 0, 0]
        result = np.count_nonzero(np.all(out_img == sought, axis=2))

        if pngDir is not None:
            nameDiff = pngDir + "/" + name + "." + str(result) + ".png"
            is_success, im_buf_arr = cv2.imencode(".png", out_img)
            im_buf_arr.tofile(nameDiff)

        return
