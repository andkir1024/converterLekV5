import cv2

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
