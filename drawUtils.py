import cv2
import numpy as np

class cvDraw:
    def show_testImage(nameImage, container, scale):
        # afterL = cv2.imread(nameImage)
        # afterLimg = cv2.resize(afterL, (0, 0), interpolation=cv2.INTER_LANCZOS4, fx=scale, fy=scale)
        # rmain1Add = Image.fromarray(afterLimg)
        # rmain1tkAdd = ImageTk.PhotoImage(image=rmain1Add)
        # container.imgtk = rmain1tkAdd
        # container.configure(image=rmain1tkAdd)
        return

    def readImage( imgName, title):
        img = cv2.imread(imgName);  # tecno camon 19 pro (997x1280)(Размеры 166.8x74.6)
        w, h = img.shape[:2]
        title = title + (f'  viewBox h: {w} w: {h}')
        root.title(title)
        return img

    def createGray(imgOk, param0):
        imgGray = cv2.cvtColor(imgOk,cv2.COLOR_BGR2GRAY)

        imgGray  = cv2.medianBlur(imgGray,7)

        # 1 повышение резкости
        kernel = np.array([[-1,-1,-1], 
                       [-1, 39,-1],
                       [-1,-1,-1]])
        # kernel = 1/3 * kernel
        # imgGray = cv2.filter2D(imgGray, -1, kernel) 

        # 2 выделение границ
        cThr=[100,100]
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgBlur = cv2.Canny(imgBlur,cThr[0],cThr[1])
        # imgGray = cv2.bitwise_not(imgBlury)
        
        kernel = np.ones((3,3))
        # imgGray = cv2.dilate(imgGray,kernel,iterations=13)
        # imgGray = cv2.erode(imgGray,kernel,iterations=1)
        
        # img_grey  = cv2.medianBlur(img_grey,1)
        # img_grey = cv2.blur(img_grey, (3, 3))
        # return imgBlur
        return imgGray
        # return imgCanny
