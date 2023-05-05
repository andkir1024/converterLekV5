import cv2
import lekaloMain
from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog
import lekaloSvg
import lecaloUtils
# from wand.image import Image
import pillow_heif
import numpy as np
import os
import lecaloConverterUtils
from lecaloConverterUtils import cvUtils

################################### andy 
testName = None
filesDir = '../popular_graphs_interesting/'
updateImage = False
# updateImageZoom = False
imgOk = None

def getFiles():
    return os.listdir(filesDir)
def selected(event):
    global testName
    global updateImage
    # получаем индексы выделенных элементов
    selected_indices = lmainListImages.curselection()
    # получаем сами выделенные элементы
    selected_files = ",".join([lmainListImages.get(i) for i in selected_indices])
    testName = filesDir + selected_files
    updateImage = True
    return
def press_mouse(event):
    # global updateImageZoom
    x = event.x
    y = event.y
    width = rmainImage.winfo_width()-4
    height = rmainImage.winfo_height()-4
    # updateImageZoom = True
    return
            
###################################
root = Tk()
root.bind('<Escape>', lambda e: root.quit())
root.title("Лекала тестер")
# root.geometry("{}x{}+{}+{}".format(100, 100, 0, 0))
# root.geometry("+%d+%d" % (0, 0))
root.geometry("1800x900")

frame1original = Frame(master=root, bg="red")
frame1original.pack()
frame2control = Frame(master=root, bg="blue")
frame2control.pack()

# верхняя полоса экранов
# выбор файла
listFiles = getFiles()
lmainListImages = Listbox(frame1original, listvariable=Variable(value=listFiles), width=60, height=50, selectmode=SINGLE)
lmainListImages.pack(expand=1, side="left", anchor=NW, fill=X, padx=5, pady=5)
lmainListImages.bind("<<ListboxSelect>>", selected)
lmainListImages.select_set(first=0)
lmainListImages.event_generate("<<ListboxSelect>>")

# собственно картинка в реальном размере
rzoomImage = Label(frame1original, width=256, height=256)
rzoomImage.pack(side="right", padx=5, pady=5, anchor=NE)

# собственно картинка
rmainImage = Label(frame1original, width=512, height=800)
rmainImage.pack(side="right", padx=0, pady=5, anchor=N,expand=False)
# rmainImage.bind("<MouseWheel>", do_zoom)
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


def show_testImage(nameImage, container, scale):
    afterL = cv2.imread(nameImage)
    afterLimg = cv2.resize(afterL, (0, 0), interpolation=cv2.INTER_LANCZOS4, fx=scale, fy=scale)
    rmain1Add = Image.fromarray(afterLimg)
    rmain1tkAdd = ImageTk.PhotoImage(image=rmain1Add)
    container.imgtk = rmain1tkAdd
    container.configure(image=rmain1tkAdd)
    return

def show_Image( container,img, imgDefault, scale):
    if img is None:
        img = imgDefault
    img4 = cv2.resize(img, (0, 0), interpolation=cv2.INTER_LANCZOS4, fx=scale, fy=scale)

    imgRAdd = Image.fromarray(img4)
    imgtkRAdd = ImageTk.PhotoImage(image=imgRAdd)
    container.imgtk = imgtkRAdd
    container.configure(image=imgtkRAdd)

def readImage( imgName, title):
    img = cv2.imread(imgName);  # tecno camon 19 pro (997x1280)(Размеры 166.8x74.6)
    w, h = img.shape[:2]
    title = title + (f'  viewBox h: {w} w: {h}')
    root.title(title)
    return img
################################### andy
def show_frame():
    global imgOk
    global updateImage
    global testName
    global updateImageZoom
    
    if updateImage == True:
        param0 = frame2control.param0.get()
        updateImage = False
        imgOk = cv2.imdecode(np.fromfile(testName, dtype=np.uint8), cv2.IMREAD_COLOR)
        if imgOk is not None:
            maxHeight = 1024
            img_grey = cv2.cvtColor(imgOk,cv2.COLOR_BGR2GRAY)
            # img_grey  = cv2.medianBlur(img_grey,7)
            img_grey = cv2.blur(img_grey, (3, 3))
            
            cvUtils.findCircles(img_grey, imgOk, draw_conrure = param0)
            
            height = imgOk.shape[0]
            if height > maxHeight:
                scale = 1024 / height
                img = cv2.resize(imgOk, (0, 0), interpolation=cv2.INTER_LINEAR, fx=scale, fy=scale)
                imgR = Image.fromarray(img)
            else:
                imgR = Image.fromarray(imgOk)
            imgtkR = ImageTk.PhotoImage(image=imgR)
            rmainImage.imgtk = imgtkR
            rmainImage.configure(image=imgtkR)
    # if updateImageZoom == True:
    #     imgR = Image.fromarray(imgOk)
    #     imgtkR = ImageTk.PhotoImage(image=imgR)
    #     rzoomImage.imgtk = imgtkR
    #     rzoomImage.configure(image=imgtkR)
    #     updateImageZoom = False

    rmainImage.after(10, show_frame)

show_frame()
root.mainloop()