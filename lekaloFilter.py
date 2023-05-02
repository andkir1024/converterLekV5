import ctypes
import math

import cv2

import lekaloConture
import lecaloUtils
import numpy as np
import arucoSize
import lekaloSvg


def doPrepareFrameV_0(aligmentedImgGray, current_value1, current_value2, clipLimit, tileGridSize):
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(tileGridSize, tileGridSize))
    aligmentedImgGray = clahe.apply(aligmentedImgGray)
    return aligmentedImgGray


def doPrepareFrameV_1(aligmentedImgGray, current_value1, current_value2, clipLimit, tileGridSize):
    # Create a Mask with adaptive threshold
    # imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # imgBlur = cv2.medianBlur(gray, 5)
    # imgBlur = cv2.GaussianBlur(frame,(5,5),1)
    # imgBlur = cv2.GaussianBlur(aligmentedImgGray, (15, 15), 1)
    imgBlur = cv2.GaussianBlur(aligmentedImgGray, (1, 1), 1)
    imgBlur = aligmentedImgGray
    imgCanny = cv2.Canny(imgBlur, current_value1, current_value1 + 0)
    # imgCanny = cv2.Canny(imgBlur,100, 200)
    kernel = np.ones((5, 5), np.uint8)
    imgDial = cv2.dilate(imgCanny, kernel, iterations=13)
    imgThre = cv2.erode(imgDial, kernel, iterations=13)

    # th, mask = cv2.threshold(aligmentedImgGray, 127, 127, cv2.THRESH_BINARY);
    # th, mask = cv2.threshold(aligmentedImgGray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th, mask = cv2.threshold(aligmentedImgGray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # blur = cv2.GaussianBlur(aligmentedImgGray, (5, 5), 0)
    # th, mask = cv2.threshold(blur, 127, 127, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    mask = imgCanny
    # mask = imgThre
    return mask

def cannyContur(aligmentedImgGray, current_value1):
    # Create a Mask with adaptive threshold
    # imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # imgBlur = cv2.medianBlur(gray, 5)
    # imgBlur = cv2.GaussianBlur(frame,(5,5),1)
    imgBlur = cv2.GaussianBlur(aligmentedImgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, current_value1, current_value1 + 5)
    # imgCanny = cv2.Canny(imgBlur,100, 200)
    kernel = np.ones((5, 5), np.uint8)
    imgDial = cv2.dilate(imgCanny, kernel, iterations=13)
    imgThre = cv2.erode(imgDial, kernel, iterations=13)

    mask = imgCanny
    return mask

def adaptiveTresholdContur(aligmentedImgGray, Cparam = 5):
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 11)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 11)

    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 27)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 27, 29)

    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 128, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 27, 29)

    # s8
    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
    mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)

    # mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, Cparam)
    mask = cv2.adaptiveThreshold(aligmentedImgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, Cparam)
    return mask


def doPrepareFrameV_2(aligmentedImg, current_value1, current_value2, clipLimit, tileGridSize):
    mask = np.zeros(aligmentedImg.shape[:2], np.uint8)

    # нули (shape, dtype = float, order = 'C'), форма параметра представляет форму, (1,65) представляет массив с 1 строкой и 65 столбцами, dtype: тип данных, необязательный параметр, по умолчанию numpy.float64
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    rect = (1, 1, aligmentedImg.shape[1], aligmentedImg.shape[0])
    cv2.grabCut(aligmentedImg, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    cv2.imwrite('waka0.jpg', aligmentedImg)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    # mask2 [:,:, np.newaxis] увеличить размер
    img = aligmentedImg * mask2[:, :, np.newaxis]
    cv2.imwrite('waka1.jpg', aligmentedImg)
    return img


def doPrepareFrameV_3(aligmentedImg, aligmentedImgGray, current_value1, current_value2, clipLimit, tileGridSize):
    # Пороговая функция - это обработка двоичных значений
    # ret, dst = cv2.threshold(src, thresh, maxval, type)
    # Описание параметра
    # src: Входное изображение, можно ввести только одноканальное изображение, обычно изображение в оттенках серого
    # dst: Выходное изображение
    # thresh: Порог
    # maxval: когда значение пикселя превышает порог (или меньше порога, в зависимости от типа), присвоенное значение
    # type тип операции бинаризации, включая следующие 5 типов: cv2.THRESH_BINARY; cv2.THRESH_BINARY_INV; cv2.THRESH_TRUNC; cv2.THRESH_TOZERO; cv2.THRESH_TOZERO_INV
    ret, thresh = cv2.threshold(aligmentedImgGray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Сгенерировать ядро ​​3x3
    kernel = np.ones((3, 3), np.uint8)
    # Функция  # morphologyEx - это операция расширения изображения, а затем коррозия для удаления данных шума, см. https://blog.csdn.net/u010682375/article/details/70026569
    # Параметр src: изображение после бинаризации
    # Параметр op: тип морфологической операции
    # Итерации параметров: время коррозии и время расширения
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # Функция расширения - это функция расширения, аналогичная роли морфологииEx
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # Подтвердите расположение фоновой области, функция distanceTransform является преобразованием расстояния, см. Https://blog.csdn.net/liubing8609/article/details/78483667
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    # Пороговая функция - это обработка двоичных значений
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    # subtract вычисляет разницу элементов между двумя массивами или массивом и скаляром, здесь вычисляется разница между фоном и передним планом
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Отметка
    ret, markers = cv2.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0
    # водораздел реализует алгоритм водораздела
    markers = cv2.watershed(aligmentedImg, markers)
    aligmentedImg[markers == -1] = [255, 0, 0]
    # cv2.imwrite('waka2.jpg', aligmentedImg)
    return aligmentedImg


def rotateImage(image, angle, center=None, scale=1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))
    # rotated = np.flip(rotated, axis=0)

    return rotated

def get_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    l = math.sqrt(
        (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))  # Евклидово расстояние между последней и текущей точкой
    return l

def modify_tuple(t, idx, new_value):
    # `id` happens to give the memory address in CPython; you may
    # want to use `ctypes.addressof` instead.
    element_ptr = (ctypes.c_longlong).from_address(id(t) + (3 + idx)*8)
    element_ptr.value = id(new_value)
    # Manually increment the reference count to `new_value` to pretend that
    # this is not a terrible idea.
    ref_count = (ctypes.c_longlong).from_address(id(new_value))
    ref_count.value += 1

