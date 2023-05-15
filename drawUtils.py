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

def detect_contures_for_mainConture(aligmentedImgGray, minArea = 10000, maxArea = 100000000):
    mask = aligmentedImgGray.copy()
    # mask = cv2.GaussianBlur(mask,(15,15),0)
    mask = cv2.bilateralFilter(mask, 19, 75, 75)

    kernel = np.ones((5, 5), np.float32) / 25
    # mask = cv2.filter2D(mask, -1, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS )
    # contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE  )

    objects_contours = prepareContoursByAreaLen(contours, minArea, maxArea)

    return objects_contours

def prepareContoursByAreaLen(contours, minArea, maxArea):
    objects_contours = []
    for cnt in contours:
        areaLen = cv2.arcLength(cnt, False)
        area = cv2.contourArea(cnt)
        # if cnt.size <= 4:
        #     continue
        # if area > minArea and area < maxArea:
        # if area > minArea and area < maxArea:
        if areaLen > 1000:
            extCtr = (cnt,areaLen)
            objects_contours.append(extCtr)
    # objtours = sorted(objects_contours, key=cv2.contourArea)[-1]
    objects_contours.sort(key=custom_key, reverse=True)
    return objects_contours
