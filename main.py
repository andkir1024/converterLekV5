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

################################### andy 
testName = None
filesDir = '../popular_graphs_interesting/'
updateImage = False
updateImageZoom = False
imgOk = None
xZoom = 0
yZoom = 0

def getFiles():
    return os.listdir(filesDir)
def selected(event):
    global testName
    global updateImage
    global xZoom,yZoom
    # получаем индексы выделенных элементов
    selected_indices = lmainListImages.curselection()
    # получаем сами выделенные элементы
    selected_files = ",".join([lmainListImages.get(i) for i in selected_indices])
    testName = filesDir + selected_files
    xZoom = yZoom = 0
    updateImage = True
def press_mouse(event):
    global xZoom,yZoom
    global updateImageZoom
    
    rmainImage.update_idletasks()
    wl1 = rmainImage.winfo_width()
    wl2 = rmainImage.winfo_reqwidth()

    xZoom = event.x
    yZoom = event.y
    width = rmainImage.winfo_width()-4
    height = rmainImage.winfo_height()-4
    updateImageZoom = True
###################################
root = Tk()
root.bind('<Escape>', lambda e: root.quit())
root.title("Лекала тестер")
# root.geometry("{}x{}+{}+{}".format(100, 100, 0, 0))
# root.geometry("+%d+%d" % (0, 0))
root.geometry("1500x900")

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
rzoomImage = Label(frame1original, width=500, height=800)
rzoomImage.pack(side="right", padx=5, pady=5, anchor=NE)

# собственно картинка
rmainImage = Label(frame1original, width=512, height=800)
rmainImage.pack(side="right", padx=0, pady=5, anchor=N,expand=False)
rmainImage.bind("<ButtonPress-1>", press_mouse)

# slider current value
current_value1 = DoubleVar()
def slider_changed1(event):
    return
current_value2 = DoubleVar()
def slider_changed2(event):
    return
       
def export_svg():
    data = [('svg', '*.svg')]
    file_path = filedialog.asksaveasfilename(filetypes=data, defaultextension=data)
    file_path = 'f:/out.svg'
    lekaloMain.saveToSvg(imgOk,file_path)
    return

def update_image():
    global updateImage
    updateImage = True
    return

def exit():
    root.quit()

# изменение размера гдавного окна
def handle_configure(event):
    update_image()
    text="window geometry:\n" + root.geometry()
    return

rmainImage.bind("<Configure>", handle_configure)

frame2control.param0 = BooleanVar()
frame2control.param1 = BooleanVar()

btnParam0 = Checkbutton(frame2control, text="Показывать контур", variable=frame2control.param0, onvalue=1, offvalue=0, command=update_image)
btnParam0.pack(side="left",  padx="10", pady="1")
btnParam1 = Checkbutton(frame2control, text="Параметр 1", variable=frame2control.param1, onvalue=1, offvalue=0, )
btnParam1.pack(side="left",  padx="10", pady="1")

btnSvg = Button(frame2control, text="Export to SVG", command=export_svg)
btnSvg.pack(side="left",  padx="10", pady="1")

btnExit = Button(frame2control, text="Exit", command=exit, width= 20)
btnExit.pack(side="right",  padx="10", pady="1")

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

def calkScale( wScr, hScr, wImg, hImg):
    dispX = 0
    dispY = 0
    if wScr < 0:
        return 1024 / hImg,dispX,dispY
    
    coff0= wScr / hScr
    coff1= wImg / hImg
    if coff0 < coff1:
        scale = wScr / wImg
        dispY = -(hScr * scale)
        dispY = -280
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

def show_frame():
    global imgOk
    global updateImage
    global testName
    global updateImageZoom
    global xZoom,yZoom

    if updateImage == True or updateImageZoom == True:
        param0 = frame2control.param0.get()
        updateImage = False
        imgOk = cv2.imdecode(np.fromfile(testName, dtype=np.uint8), cv2.IMREAD_COLOR)
        if imgOk is not None:
            img_grey = cv2.cvtColor(imgOk,cv2.COLOR_BGR2GRAY)
            # img_grey  = cv2.medianBlur(img_grey,7)
            img_grey = cv2.blur(img_grey, (3, 3))
            
            cvUtils.findCircles(img_grey, imgOk, draw_conrure = param0)

            scale, dispX, dispY = calkScale(rmainImage.winfo_width()-4, rmainImage.winfo_height()-4, imgOk.shape[1], imgOk.shape[0])
            
            img = cv2.resize(imgOk, (0, 0), interpolation=cv2.INTER_LINEAR, fx=scale, fy=scale)
            rectView = calkSizeViewRect(xZoom, yZoom, rzoomImage, scale, dispX, dispY)
            if rectView is not None:
                img = cv2.rectangle(img, rectView[0], rectView[1], (0, 255, 0), 2)
            
            imgR = Image.fromarray(img)
            imgtkR = ImageTk.PhotoImage(image=imgR)
            rmainImage.imgtk = imgtkR
            rmainImage.configure(image=imgtkR)

            # scale = 0.25*2
            scaleZoom = 1
            img = cv2.resize(imgOk, (0, 0), interpolation=cv2.INTER_LINEAR, fx=scaleZoom, fy=scaleZoom)
            viewX = int(xZoom / scale)
            viewY = int(yZoom / scale)
            im_crop = img[viewY:viewY+500, viewX:viewX+1500]
            # im_crop = img[viewY:viewY+500, viewX:viewX+500]
            # im_crop = img[0:500, 0:500]
            # crop_img = img[y:y+h, x:x+w]
            imgR = Image.fromarray(im_crop)
            imgtkZoom = ImageTk.PhotoImage(image=imgR)
            rzoomImage.imgtk = imgtkZoom
            rzoomImage.configure(image=imgtkZoom)
            updateImageZoom = False

    rmainImage.after(10, show_frame)

show_frame()
root.mainloop()