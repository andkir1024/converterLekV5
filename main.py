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

################################### andy 22222 33333 old branch
testName = None
def getFiles():
    return os.listdir('../popular_graphs_interesting/')
def selected(event):
    # получаем индексы выделенных элементов
    selected_indices = lmain.curselection()
    # получаем сами выделенные элементы
    selected_files = ",".join([lmain.get(i) for i in selected_indices])
    msg = f"вы выбрали: {selected_files}"
    return
    # selection_label["text"] = msg
    
###################################
root = Tk()
root.bind('<Escape>', lambda e: root.quit())
root.title("Лекала тестер")
# root.geometry("{}x{}+{}+{}".format(100, 100, 0, 0))
root.geometry("+%d+%d" % (0, 0))

frame1original = Frame(master=root, bg="red")
frame1original.pack()
frame2control = Frame(master=root, bg="blue")
frame2control.pack()

# верхняя полоса экранов
# выбор файла
listFiles = getFiles()
lmain = Listbox(frame1original, listvariable=Variable(value=listFiles), width=60, height=50, selectmode=SINGLE)
lmain.pack(expand=1, side="left", anchor=NW, fill=X, padx=5, pady=5)
lmain.select_set(first=0)
lmain.bind("<<ListboxSelect>>", selected)

# собственно картинка
rmain = Label(frame1original)
rmain.pack(side="right", padx=10, pady=1)

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

def exit():
    root.quit()

frame2control.param0 = BooleanVar()
frame2control.param1 = BooleanVar()

btnParam0 = Checkbutton(frame2control, text="Параметр 0", variable=frame2control.param0, onvalue=1, offvalue=0, )
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
    global testName
    testName = imgName
    img = cv2.imread(imgName);  # tecno camon 19 pro (997x1280)(Размеры 166.8x74.6)
    w, h = img.shape[:2]
    title = title + (f'  viewBox h: {w} w: {h}')
    root.title(title)
    return img
################################### andy
def show_frame():
    global panelA, panelB
    global imgOk

    global testName
    if (testName is None)==True:
        img = readImage("test32.jpg", 's8+ (Размеры 160×73)')
    else:
        img = cv2.imread(testName);
    rval = True

    if rval == True:
        imgTemp = img.copy()
        param0 = frame2control.param0.get()
        param1 = frame2control.param1.get()
        addedW = 0
        if param0 == True:
            addedW = 2
        addedH = 0
        if param1 == True:
            addedW = -2
        params = (addedW, addedH)

        imgR = Image.fromarray(img)
        imgtkR = ImageTk.PhotoImage(image=imgR)
        rmain.imgtk = imgtkR
        rmain.configure(image=imgtkR)


    rmain.after(10, show_frame)

show_frame()
root.mainloop()