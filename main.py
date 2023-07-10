import getopt, sys
import cv2
from tkinter import *
from PIL import Image, ImageDraw
from PIL import ImageTk
from tkinter import filedialog
import lekaloSvg
import numpy as np
import os
from lecaloConverterUtils import cvUtils
from drawUtils import cvDraw
import datetime
from bezier import bezier, contoureAnalizer, FigureStatus

################################### разборка аргументов
testName = None
filesDir = '../popular1/'
filesSrc = None
svgDir = None
# '../outSvg/'
cmpDir = '../outSvg/'
pngDir = None
doConsole = True
dpiSvg = 9.977

argumentList = sys.argv[1:]
options = "hmo:"
long_options = ["Help", "wnd", "dirSrc=","pngDir=","dirDst=", "svg=", "cmp="]
arguments, values = getopt.getopt(argumentList, options, long_options)
for currentArgument, currentValue in arguments:
        if currentArgument in ("-o", "--dirDst"):
            svgDir = currentValue
        if currentArgument in ("-d", "--dirSrc"):
            filesDir = currentValue
        if currentArgument in ("-p", "--pngDir"):
            pngDir = currentValue
        elif currentArgument in ("-w","--wnd"):
            doConsole = False
        if currentArgument in ("-s", "--svg"):
            dpiSvg = float(currentValue)
        if currentArgument in ("-c", "--cmp"):
            dpiSvg = float(currentValue)
    
updateImage = False
updateImageZoom = False
imgOk = None
xZoom = 0
yZoom = 0

def getFiles():
    if os.path.isdir(filesDir) == True:
        files = []
        for f in os.scandir(filesDir):
            if f.is_file() and f.path.split('.')[-1].lower() == 'png':
                files.append(f.path)
        return files
    return None
def selected(event):
    global testName
    global updateImage
    global xZoom,yZoom
    global imgOk
    global filesSrc
    # получаем индексы выделенных элементов
    selected_indices = lmainListImages.curselection()
    # получаем сами выделенные элементы
    filesSrc  = ",".join([lmainListImages.get(i) for i in selected_indices])
    # filesName = filesDir + filesSrc
    xZoom = yZoom = 0
    imgOk = cv2.imdecode(np.fromfile(filesSrc, dtype=np.uint8), cv2.IMREAD_COLOR)
    updateImage = True
def press_mouse(event):
    global xZoom,yZoom
    global updateImageZoom
    if imgOk is None:
        return
    xZoom = event.x
    yZoom = event.y
    updateImageZoom = True
###################################
if doConsole == False:
    root = Tk()
    root.bind('<Escape>', lambda e: root.quit())
    root.title("Лекала тестер")
    root.geometry("1700x1000+0+0")

    frame1original = Frame(master=root, bg="red")
    frame1original.pack()
    frame2control = Frame(master=root, bg="blue")
    frame2control.pack()

    # верхняя полоса экранов
    # выбор файла
    listFiles = getFiles()
    lmainListImages = Listbox(frame1original, listvariable=Variable(value=listFiles), width=60, height=50, selectmode=SINGLE)
    lmainListImages.pack(expand=1, side="left", anchor=NW, fill=X, padx=5, pady=5)

    # собственно картинка в реальном размере
    rzoomImage = Label(frame1original, width=800, height=800)
    rzoomImage.pack(side="right", padx=5, pady=5, anchor=NE)

    # собственно картинка
    rmainImage = Label(frame1original, width=512, height=800)
    rmainImage.pack(side="right", padx=0, pady=5, anchor=N,expand=False)
    rmainImage.bind("<ButtonPress-1>", press_mouse)

    # slider current value
    current_value1 = DoubleVar()
    current_value2 = DoubleVar()
def slider_changed1(event):
    update_image()
    return
def slider_changed2(event):
    update_image()
    return
def export_svg():
    return
    
def update_image():
    global updateImage
    updateImage = True
    return
def exit():
    root.quit()
# изменение размера гдавного окна
def handle_configure(event):
    # update_image()
    text="window geometry:\n" + root.geometry()
    return

if doConsole == False:
    rmainImage.bind("<Configure>", handle_configure)

    frame2control.param0 = BooleanVar()
    frame2control.param1 = BooleanVar()

    btnParam0 = Checkbutton(frame2control, text="Показывать контур", variable=frame2control.param0, onvalue=1, offvalue=0, command=update_image)
    btnParam0.pack(side="left",  padx="10", pady="1")
    btnParam1 = Checkbutton(frame2control, text="Параметр 1", variable=frame2control.param1, onvalue=1, offvalue=0, )
    btnParam1.pack(side="left",  padx="10", pady="1")

    btnExit = Button(frame2control, text="Exit", command=exit, width= 20)
    btnExit.pack(side="right",  padx="10", pady="1")

    btnSvg = Button(frame2control, text="Export to SVG", command=export_svg, width= 20)
    btnSvg.pack(side="right",  padx="10", pady="1")

    slider1 = Scale( frame2control,from_=1, to=250, orient='horizontal',  command=slider_changed1, variable=current_value1, length = 200)
    slider1.set(200)
    slider1.pack(side="left",  padx="10", pady="1")

    slider2 = Scale( frame2control,from_=1, to=100, orient='horizontal',  command=slider_changed2, variable=current_value2, length = 200)
    slider2.set(30)
    slider2.pack(side="left",  padx="10", pady="1")

    # генерация выбора первого элемента в списке каритнок
    lmainListImages.bind("<<ListboxSelect>>", selected)
    lmainListImages.select_set(first=0)
    lmainListImages.event_generate("<<ListboxSelect>>")

def calkViewParam( label, image):
    dispX = 0
    dispY = 0
    rmainImage.update_idletasks()
    hScr = label.winfo_height()
    wScr = label.winfo_width()
    wImg = image.shape[1]
    hImg = image.shape[0]
    
    if wScr < 10:
        return 1024 / hImg,dispX,dispY
    
    coff0= wScr / hScr
    coff1= wImg / hImg
    if coff0 < coff1:
        scale = wScr / wImg
        dispY = -(hScr - (hImg * scale))/2
        # dispY = -280
    else:
        scale = hScr / hImg
        dispX = -(wScr * scale)
    
    return scale, dispX, dispY
def calkSizeViewRect(xZoom, yZoom, label, scale, dispX, dispY):
    if label.winfo_height() < 10:
        return None
    xZoom = xZoom + dispX
    yZoom = yZoom + dispY
    heightZoom = label.winfo_height() * scale
    widthZoom = label.winfo_width() * scale
    return [(int(xZoom),int(yZoom)),(int(xZoom + widthZoom), int(yZoom + heightZoom))]
def convertScreenToImageCoord(rmainImage, imgOk, xZoom, yZoom):
    scale, dispX, dispY = calkViewParam(rmainImage, imgOk)
    deltaX = xZoom + dispX
    if deltaX < 0:
        deltaX = 0
        
    deltaY = yZoom - dispY
    if deltaY < 0:
        deltaY = 0

    viewX = int(deltaX / scale)
    viewY = int(deltaY / scale)
    # viewX = 440
    # viewY = 934
    return viewX, viewY
def do_frame(imgOk, filesSrc, svgDir, param0,pngDir):
    # imgDraw = imgOk.copy()
    # # param0 = frame2control.param0.get()  
    # imgGrey =cvDraw.createGray(imgOk, param0)
    # imgTst = cvUtils.doContours(imgGrey, imgDraw, filesSrc, svgDir, dpiSvg)
    # return imgDraw, imgDraw, False
    # canExeption = False
    if bezier.DEBUG_MODE == False:    
        try:
            imgDraw = imgOk.copy()
            # param0 = frame2control.param0.get()
            imgGrey =cvDraw.createGray(imgOk, param0)
            imgTst = cvUtils.doContours(imgGrey, imgDraw, filesSrc, svgDir, dpiSvg,pngDir)
        except Exception as e:
            return imgDraw, imgDraw, e
        return imgDraw, imgTst, None
    else:
        imgDraw = imgOk.copy()
        imgGrey =cvDraw.createGray(imgOk, param0)
        imgTst = cvUtils.doContours(imgGrey, imgDraw, filesSrc, svgDir, dpiSvg,pngDir)
        return imgDraw, imgTst, None
def show_frame():
    global imgOk
    global updateImage
    global testName
    global updateImageZoom
    global xZoom,yZoom
    global filesSrc, svgDir, pngDir

    if updateImage == True or updateImageZoom == True:
        updateImage = False
        if imgOk is not None:
            imgDraw,imgTst, resImag = do_frame(imgOk, filesSrc, svgDir, slider1.get(),pngDir)

            scale, dispX, dispY = calkViewParam(rmainImage, imgDraw)
            img = cv2.resize(imgDraw, (0, 0), interpolation=cv2.INTER_AREA, fx=scale, fy=scale)
            rectView = calkSizeViewRect(xZoom, yZoom, rzoomImage, scale, dispX, dispY)
            if rectView is not None:
                img = cv2.rectangle(img, rectView[0], rectView[1], (0, 255, 0), 2)
            
            # kernel = np.ones((3,3))
            # img = cv2.erode(img,kernel,iterations=1)
            
            imgR = Image.fromarray(img)
            imgtkR = ImageTk.PhotoImage(image=imgR)
            rmainImage.imgtk = imgtkR
            rmainImage.configure(image=imgtkR)

            viewX, viewY = convertScreenToImageCoord(rmainImage, imgOk, xZoom, yZoom)
            heightZoom = rzoomImage.winfo_height()
            widthZoom = rzoomImage.winfo_width()
            height = imgOk.shape[0]
            width = imgOk.shape[1]
            right = viewX+widthZoom 
            if right > width:
                right = width
                viewX = right-widthZoom

            # imgDraw = cv2.imdecode(np.fromfile("example.png", dtype=np.uint8), cv2.IMREAD_COLOR)
            
            im_crop = imgDraw[viewY:viewY+heightZoom, viewX:right]
            # im_crop = imgTst[viewY:viewY+heightZoom, viewX:right]
            cv2.imwrite("imgTst.png", imgTst)

            imgR = Image.fromarray(im_crop)
            imgtkZoom = ImageTk.PhotoImage(image=imgR)
            rzoomImage.imgtk = imgtkZoom
            rzoomImage.configure(image=imgtkZoom)
            updateImageZoom = False
            
    rmainImage.after(100, show_frame)

if doConsole == False:
    show_frame()
    bezier.DEBUG_MODE = True
    root.mainloop()
else:
    bezier.DEBUG_MODE = False
    listFiles = getFiles()
    if listFiles is None:
        print(filesDir + " - директория пуста или отсутсявует")
    else:
        nowStart = datetime.datetime.now()
        index = 0
        listErr = []
        for f in listFiles:
            imgOk = cv2.imdecode(np.fromfile(f, dtype=np.uint8), cv2.IMREAD_COLOR)
            imd0, img1, ok = do_frame(imgOk, f, svgDir, 0, pngDir)
            if ok is None:
                msg = f"{index} "
                print(msg + f)
            else:
                print(ok)
                listErr.append(ok)
                msg = 'файл дефектный:'+f
                print(msg)
                listErr.append(msg)
            index = index + 1
        now = datetime.datetime.now()
        tdelta = (now - nowStart).total_seconds()
        print(f"Завершена за: {tdelta} сек")
        if len(listErr) > 0:
            print(f"Произошли ошибки:")
        for err in listErr:
            print(err)
