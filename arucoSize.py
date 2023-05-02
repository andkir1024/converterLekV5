import cv2 as cv
import numpy as np

def arucoWarp(frame):
    try:
        # Load the dictionary that was used to generate the markers.
        # dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)
        dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_5X5_50)

        # Initialize the detector parameters using default values
        parameters = cv.aruco.DetectorParameters_create()

        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(frame, dictionary, parameters=parameters)

        '''
        index = np.squeeze(np.where(markerIds == 12));
        refPt1 = np.squeeze(markerCorners[index[0]])[3];

        index = np.squeeze(np.where(markerIds == 10));
        refPt2 = np.squeeze(markerCorners[index[0]])[0];
        
        index = np.squeeze(np.where(markerIds == 11));
        refPt3 = np.squeeze(markerCorners[index[0]])[1];

        index = np.squeeze(np.where(markerIds == 13));
        refPt4 = np.squeeze(markerCorners[index[0]])[2];
        '''

        # zz = np.where(markerIds == 12)
        index = np.squeeze(np.where(markerIds == 12));
        refPt1 = np.squeeze(markerCorners[index[0]])[1];

        index = np.squeeze(np.where(markerIds == 10));
        refPt2 = np.squeeze(markerCorners[index[0]])[2];

        index = np.squeeze(np.where(markerIds == 11));
        refPt3 = np.squeeze(markerCorners[index[0]])[3];

        index = np.squeeze(np.where(markerIds == 13));
        refPt4 = np.squeeze(markerCorners[index[0]])[0];

        distance = np.linalg.norm(refPt3 - refPt2);

        pts_src = np.zeros((4, 2), dtype="float32")
        pts_src[0]=refPt1
        pts_src[1]=refPt2
        pts_src[2]=refPt3
        pts_src[3]=refPt4

        # pts = np.array(pts_src)
        # warped = four_point_transform(frame, pts)
        # rect = points_to_rect_int(pts_src)
        # (x, y), (w, h), angle = rect

        scaleSize = 2
        newW = 400*scaleSize
        newH = 800*scaleSize
        # pts_dst = np.array([[0, 0], [newW, 0], [newW, newH], [0, newH]])
        pts_dst = np.array([[0, 0], [0, newH], [newW, newH], [newW, 0]])
        h, status = cv.findHomography(pts_src, pts_dst)
        warped = cv.warpPerspective(frame, h, (newW, newH))
        warped = np.rot90(warped)
        # cv.imwrite('qq.png', im_out)

        # warped = addBorderForImage(warped, 40)
        # cv.imwrite('qq.png', warped)

        return (warped, markerCorners, markerIds)

    except Exception as inst:
        print(inst)
        return (None, 'Не найдены или поврежденные маркеры', None)
    return (None, 'No markers', None)

def points_to_rect_int(pts):
    rect = np.zeros((4, 2), dtype="int32")
    rect[0] = (int)(pts[0])
    rect[1] = (int)(pts[1])
    rect[2] = (int)(pts[2])
    rect[3] = (int)(pts[3])
    return rect
def points_to_rect(pts):
    rect = np.zeros((4, 2), dtype="float32")
    rect[0] = pts[0]
    rect[1] = pts[1]
    rect[2] = pts[2]
    rect[3] = pts[3]
    return rect


def order_points(pts):
    try:
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype="float32")
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect
    except Exception as inst:
        print(inst)
        return None


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    # rect = order_points(pts)
    rect = points_to_rect(pts)

    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    # compute the perspective transform matrix and then apply it
    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped

# определение размеров на выровненой каритнке
def arucoMeasurement(frame):
    try:
        # Load the dictionary that was used to generate the markers.
        # dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)
        dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_5X5_50)

        # Initialize the detector parameters using default values
        parameters = cv.aruco.DetectorParameters_create()

        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(frame, dictionary, parameters=parameters)

        index = np.squeeze(np.where(markerIds == 12));
        refPt1 = np.squeeze(markerCorners[index[0]])[1];

        index = np.squeeze(np.where(markerIds == 10));
        refPt2 = np.squeeze(markerCorners[index[0]])[2];
        #
        index = np.squeeze(np.where(markerIds == 11));
        refPt3 = np.squeeze(markerCorners[index[0]])[3];

        index = np.squeeze(np.where(markerIds == 13));
        refPt4 = np.squeeze(markerCorners[index[0]])[0];


        pts_dstNew = np.zeros((4, 2), dtype="float32")
        pts_dstNew[0]=refPt1
        pts_dstNew[1]=refPt2
        pts_dstNew[2]=refPt3
        pts_dstNew[3]=refPt4

        pts = np.array(pts_dstNew)
        warped = four_point_transform(frame, pts)

        return (warped, markerCorners, markerIds)

    except Exception as inst:
        print(inst)
        return (None, 'Не найдены или поврежденные маркеры', None)
    return (None, 'No markers', None)

def diatancePoints(pointA, pointB):
    return
def distanceCalculate(p1,p2):  # p1 and p2 in format (x1,y1) and (x2,y2) tuples
    dis=((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)**0.5
    dis=abs(dis)   #removing negative sign.
    return dis
# определение нвправвления камеры на телефон
def viewDirection(aligmentedImg, markers, markerIds):
    distMarkers = 16.0
    height, width = aligmentedImg.shape[:2]
    marker10 = findMarkerById(markers, markerIds, 10)
    marker11 = findMarkerById(markers, markerIds, 11)
    marker12 = findMarkerById(markers, markerIds, 12)
    marker13 = findMarkerById(markers, markerIds, 13)
    tl =markers[0][0][0]
    tr =markers[1][0][0]
    bl =markers[2][0][0]
    br =markers[3][0][0]
    pts1 = np.float32(tl)

    distTop = distanceCalculate(tl, tr)
    distBase1 = distanceCalculate(tl, bl)
    distBase2 = distanceCalculate(tr, br)
    return

# определение нвправвления камеры на телефон
def findMarkerById(markers, markerIds, Id):
    for index in range(0,4):
        testId = markerIds[index][0]
        if testId == Id:
            return markers[index][0]
    return None

def addBorderForImage(img, border):
    width, height = img.shape[:2]
    blank_image = np.zeros((width + (border*2), height + (border*2), 3), np.uint8)
    blank_image[:] = (255, 0, 255)
    # blank_image[border:border] = img
    # blank_image[40:40, width:height] = img
    ROI = img[40:width, 40:height]
    x_offset = y_offset = 20
    blank_image[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img

    # blank_image = img[40:width, 40:height]
    return blank_image
    # blank_image[x:width + 100, y:height + 100] = img
    # blank_image.paste(img, (border, border))
    # return blank_image

widthAll =[]
distAll =[]
def arucoGetSize(img, markers, markerIds):
    width, height = img.shape[:2]
    # width = width + 6
    # width = height+  6
    distMarkersW = 14.55
    distMarkersH = 22.5
    coffW = width/ distMarkersW
    coffH = height/ distMarkersH
    distMarkersW1 = width / coffH
    distMarkersH1 = height / coffW

    marker10 = findMarkerById(markers, markerIds, 10)[0]
    marker11 = findMarkerById(markers, markerIds, 11)[0]
    marker12 = findMarkerById(markers, markerIds, 12)[0]
    distTop = distanceCalculate(marker10, marker11)
    distWidth = distanceCalculate(marker10, marker12)

    widthAll.append(int(width))
    distAll.append(int(distTop))
    return

def myRound(n):
    answer = round(n)
    if not answer%2:
        return int(answer)
    if abs(answer+1-n) < abs(answer-1-n):
        return int(answer + 1)
    else:
        return int(answer - 1)
