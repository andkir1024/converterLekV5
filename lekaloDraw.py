import math
import os
import glob

import cv2

import lecaloUtils
import lekaloFilter
import numpy as np
import arucoSize
from numpy import unravel_index


def drawCircles(circles, img):
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(img, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(img, center, radius, (255, 0, 255), 3)
    return

def drawContures(contours, img, thickness = 1):
    for cntExt in contours:
        cnt = cntExt[0]
        cv2.drawContours(img, [cnt], 0, (255, 0, 0), thickness)
    return

def drawLines(lines, img, minShowsize = 100):
    if (lines is None) == True:
        return
    for line in lines:
        for x1, y1, x2, y2 in line:
            dist = lekaloFilter.get_distance((x1,y1), (x2, y2))
            if dist > minShowsize:
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 1)

def drawConturePhone(conturePhone, img, w, h, pixel_cm_ratio):
    # return
    ptsDisp=  [conturePhone[4], conturePhone[5]]
    round = conturePhone[6]

    pts0= [conturePhone[0], conturePhone[2]]
    pts1= [conturePhone[1], conturePhone[2]]
    pts2= [conturePhone[1], conturePhone[3]]
    pts3= [conturePhone[0], conturePhone[3]]

    points = np.array([pts0, pts1, pts2, pts3])
    points = points + ptsDisp
    poly = np.int32([points])
    cv2.polylines(img, poly, 1, (255, 0, 255), 1)
    startPts = [pts0[0]  + ptsDisp[0], pts0[1] + ptsDisp[1]]
    endPts = [startPts[0] + round, startPts[1] + round]
    endRectPts = [startPts[0] + round, startPts[1] + round]

    # закругление углов
    cv2.rectangle(img, startPts, endPts, (255, 0, 0), -1)
    hPhone = conturePhone[3]-conturePhone[2]
    # radius = (2.414 * round) / (hPhone/2)
    # radius = (3 * round) / (hPhone/2)
    radius = (3.5 * round) / (hPhone/2)

    rounded_rectangle(img, (points[0][0],points[0][1]), (points[2][1],points[2][0]+0), color=(255, 255, 0), radius=radius, thickness=2, dispX=0, dispY=0)
    printInfo(img, w, h, pixel_cm_ratio)
    return

def printInfo(img, w, h, pixel_cm_ratio):
    object_width = w / pixel_cm_ratio
    object_height = h / pixel_cm_ratio
    wScreen, hScreen = img.shape[:2]
    posX = (int)(wScreen/4)
    posY = (int)(hScreen/4)
    cv2.putText(img, "W {} mm".format(round(10 * object_width, 2)), (posY, posX), cv2.FONT_HERSHEY_PLAIN, 2,(255, 255, 255), 2)
    posX = posX + 30
    cv2.putText(img, "H {} mm".format(round(10 * object_height, 2)), (posY, posX), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

def drawFinalContures(conturePhone, contureHoles, img, thickness):
    if (contureHoles is None) == False:
        # Draw objects
        # mainParam = resultCnt[0]
        # _, w, h, pixel_cm_ratio, dispX, dispY = mainParam
        # printInfo(img, w, h, pixel_cm_ratio)
        ptsDisp = [conturePhone[4], conturePhone[5]]

        for cntExt in contureHoles:
            type = cntExt[0]
            fig = cntExt[1]
            if type == 'c':
                disp = int(fig[3])
                center = (disp+ptsDisp[0] +int(fig[0]), ptsDisp[1]+int(fig[1]))
                radius = int(fig[2])
                if center[0]+radius > conturePhone[1]+ptsDisp[0]:
                    continue
                cv2.circle(img, center, radius, (0, 255, 0), thickness)
                continue
            if type == 'm':
                top_left = fig[0]
                bottom_right = fig[1]
                rounded_rectangle(img, top_left, bottom_right, color=(255, 0, 0), radius=fig[2], thickness=thickness, dispX = 0, dispY = 0)
                continue
            if type == 'b':
                disp = int(fig[3])
                top_left1 = (fig[0][0],fig[0][1])
                bottom_right1 = (fig[1][1],fig[1][0])

                top_left = (fig[0][0] + disp + ptsDisp[0], fig[0][1] + ptsDisp[1])
                bottom_right = (fig[1][1] + ptsDisp[1], fig[1][0] + disp + ptsDisp[0])
                radius = int(fig[2])

                rightRect = bottom_right[1]
                if rightRect >= conturePhone[1]+ptsDisp[0]:
                    continue

                rounded_rectangle(img, top_left, bottom_right, color=(0, 0, 255), radius=radius, thickness=thickness, dispX = 0, dispY = 0)
                # rounded_rectangle(img, top_left1, bottom_right1, color=(0, 0, 255), radius=radius, thickness=thickness, dispX = 0, dispY = 0)
                # rounded_rectangle(img, (fig[0][0],fig[0][1]), (fig[1][1],fig[1][0]), color=(0, 0, 255), radius=fig[2], thickness=thickness, dispX = 0, dispY = 0)
                continue

def rounded_rectangle(src, top_left, bottom_right, radius=1, color=255, thickness=1, line_type=cv2.LINE_AA, dispX = 0, dispY = 0):
    #  corners:
    #  p1 - p2
    #  |     |
    #  p4 - p3

    p1 = top_left
    p2 = (bottom_right[1], top_left[1])
    p3 = (bottom_right[1], bottom_right[0])
    p4 = (top_left[0], bottom_right[0])

    height = abs(bottom_right[0] - top_left[1])

    if radius > 1:
        radius = 1

    corner_radius = int(radius * (height/2))

    if thickness < 0:

        #big rect
        top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
        bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

        top_left_rect_left = (p1[0], p1[1] + corner_radius)
        bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

        top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
        bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

        all_rects = [
        [top_left_main_rect, bottom_right_main_rect],
        [top_left_rect_left, bottom_right_rect_left],
        [top_left_rect_right, bottom_right_rect_right]]

        [cv2.rectangle(src, rect[0], rect[1], color, thickness) for rect in all_rects]

    # draw straight lines
    cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
    cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
    cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
    cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, color ,thickness, line_type)
    cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, color , thickness, line_type)
    cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,   color , thickness, line_type)
    cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,  color , thickness, line_type)

    return src