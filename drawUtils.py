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

        cThr=[100,100]
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
        imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
        
        kernel = np.ones((5,5))
        imgDial = cv2.dilate(imgCanny,kernel,iterations=3)
        imgThre = cv2.erode(imgDial,kernel,iterations=3)
        
        # img_grey  = cv2.medianBlur(img_grey,1)
        # img_grey = cv2.blur(img_grey, (3, 3))
        # return imgBlur
        return imgGray
        # return imgCanny
