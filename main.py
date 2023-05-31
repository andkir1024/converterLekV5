import getopt, sys
import cv2
import lekaloMain
from tkinter import *
from PIL import Image, ImageDraw
from PIL import ImageTk
from tkinter import filedialog
import lekaloSvg
import lecaloUtils
import pillow_heif
import numpy as np
import os
import lecaloConverterUtils
from lecaloConverterUtils import cvUtils
from drawUtils import cvDraw
import datetime

################################### разборка аргументов
testName = None
filesDir = '../popular1/'
filesSrc = None
svgDir = '../outSvg/'
doConsole = True
dpiSvg = 9.066

argumentList = sys.argv[1:]
options = "hmo:"
long_options = ["Help", "wnd", "dirSrc=", "svg="]
arguments, values = getopt.getopt(argumentList, options, long_options)
for currentArgument, currentValue in arguments:
        if currentArgument in ("-d", "--dirSrc"):
            filesDir = currentValue
        elif currentArgument in ("-w","--wnd"):
            doConsole = False
        if currentArgument in ("-s", "--svg"):
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
    root.geometry("1700x900+0+0")

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
    global filesSrc
    if imgOk is None:
        return
    # data = [('svg', '*.svg')]
    # file_path = filedialog.asksaveasfilename(filetypes=data, defaultextension=data)
    # file_path = 'f:/out.svg'
    fileDst = os.path.splitext(filesSrc)
    if not os.path.exists(svgDir):
        os.mkdir(svgDir)
    filename = fileDst[0].split('/')
    fileDst = svgDir + filename[-1] + ".svg"
    lekaloSvg.saveToSvg(imgOk,fileDst)
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
def do_frame(imgOk, filesSrc, svgDir):
    imgDraw = imgOk.copy()
    param0 = frame2control.param0.get()
    imgGrey =cvDraw.createGray(imgOk, slider1.get())
    # cvUtils.findCircles(imgGrey, imgDraw, draw_conrure = param0)
    # выделение глапвного контура
    imgTst = cvUtils.doContours(imgGrey, imgDraw, filesSrc, svgDir, dpiSvg)
    # imgTst,finalCountours = cvUtils.getMainContours(imgGrey, imgDraw)
    # cvUtils.getContours1(imgGrey, imgDraw)
    # cvUtils.findLines(imgGrey, imgDraw, draw_conrure = param0)
    return imgDraw
def show_frame():
    global imgOk
    global updateImage
    global testName
    global updateImageZoom
    global xZoom,yZoom
    global filesSrc, svgDir

    if updateImage == True or updateImageZoom == True:
        updateImage = False
        if imgOk is not None:
            imgDraw = do_frame(imgOk, filesSrc, svgDir)

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

            imgR = Image.fromarray(im_crop)
            imgtkZoom = ImageTk.PhotoImage(image=imgR)
            rzoomImage.imgtk = imgtkZoom
            rzoomImage.configure(image=imgtkZoom)
            updateImageZoom = False
            
    rmainImage.after(100, show_frame)

if doConsole == False:
    show_frame()
    root.mainloop()
else:
    listFiles = getFiles()
    if listFiles is None:
        print(filesDir + " - директория пуста или отсутсявует")
    else:
        nowStart = datetime.datetime.now()
        for f in listFiles:
            imgOk = cv2.imdecode(np.fromfile(f, dtype=np.uint8), cv2.IMREAD_COLOR)
            # do_frame(imgOk, f, svgDir)
            print(f)
        now = datetime.datetime.now()
        tdelta = (now - nowStart).total_seconds()
        print(f"Завершена за: {tdelta} сек")
