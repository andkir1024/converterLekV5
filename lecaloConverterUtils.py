import cv2
# import cvUtils

class cvUtils:
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
