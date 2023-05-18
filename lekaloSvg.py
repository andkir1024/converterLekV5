import math
import cv2
import numpy as np

def saveToSvg(imgOk,nameSvg):
    return
    cntExt = []
    conturToSvg(cntExt, nameSvg)
    return
def createCirclePath(cx, cy, r):
    x = cx-r
    y = cy
    d = 2 * r
    # strPath = f'<path class="fil0 str0" d="M {x}, {y} a {r},{r} 0 1,1 {d},0 a {r},{r} 0 1,1 -{d},0"/>'
    strPath = f'\t<path fill="none" stroke-width="1" stroke="red"  d="M {x}, {y} a {r},{r} 0 1,1 {d},0 a {r},{r} 0 1,1 -{d},0"/>\n'

    return strPath

def createRectPath(cx, cy, r):
    x = cx-r
    y = cy
    d = 2 * r
    strPath = f'\t<path fill="none" stroke-width="1" stroke="red"  d="M10 10 H 90 V 90 H 10 L 10 10"/>\n'

    return strPath


def roundRectSvg(cnt, coff):
    # <rect class="fil0 str0" x="50" y="20" rx="100" ry="100" width="450" height="450"/>
    # x1 = cnt[0][0]
    # y1 = cnt[0][1]
    #
    # x2 = cnt[1][0]
    # y2 = cnt[1][1]
    x1 = cnt[0]
    y1 = cnt[2]
    x2 = cnt[1]
    y2 = cnt[3]

    width = x2 - x1
    height  = y2 - y1

    # r = cnt[6] * width / 4
    round = cnt[6]
    r = 1.22 * round * coff / 4
    r = round * coff / (2 *1.22)
    # radius = (3 * round) / (height / 2)
    # r1 = round / height

    str = f'\t<rect class="fil0 str0" x="0" y="0" rx="{r}" ry="{r}"  width="{width}"  height="{height}"/>\n'
    # str = f'\t<rect class="fil0 str0" x="{x1}" y="{y1}" rx="{r}" ry="{r}"  width="{width}"  height="{height}"\>\n'
    return str
def circleSvg(cnt, coff, object_disp, object_startX,mainContureTop):
    x = cnt[0]
    y = cnt[1]
    r = cnt[2]
    disp = cnt[3]
    x = x + disp
    str = f'\t<circle class="fil0 str0" cx="{x}" cy="{y}" r="{r}"/>\n'
    # center = (disp + ptsDisp[0] + int(fig[0]), ptsDisp[1] + int(fig[1]))
    if x + r + object_disp > mainContureTop + object_disp:
        return None

    return str

def boxSvg(cnt, coff, object_disp, object_startX):
    x1 = cnt[0][0]
    y1 = cnt[0][1]

    x2 = cnt[1][0]
    y2 = cnt[1][1]

    width = x2 - x1
    height  = y2 - y1

    # r = cnt[2] * width / 4
    r = width / 3
    disp = cnt[3]
    x1 = x1 + disp
    x2 = x2 + disp

    str = f'\t<rect class="fil0 str0" x="{x1}" y="{y1}" rx="{r}" ry="{r}"  width="{width}"  height="{height}"/>\n'
    return str

def conturToSvg(cntExt, nameSvg, object_width = 100, object_height = 200, coff = 0.1):
    with open(nameSvg, "w+") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{round(object_width/coff, 3)}mm" height="{round(object_height/coff, 3)}mm"  version="1.1"\n')
        f.write(f'style="shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd"\n')
        # f.write(f'viewBox="{object_startX} {object_startY}  {object_width} {object_height}"\n')
        f.write(f'viewBox="0 0  {object_width} {object_height}"\n')
        f.write('xmlns:xlink="http://www.w3.org/1999/xlink">\n')

        f.write('\n')
        f.write('<defs>\n')
        f.write('<style type="text/css">\n')
        f.write('<![CDATA[\n')
        f.write('.str0 {stroke:#2B2A29;stroke-width:2.84;stroke-miterlimit:22.9256}\n')
        f.write('.fil0 {fill:none}\n')
        f.write(']]>\n')
        f.write('</style>\n')
        f.write('</defs>\n')
        f.write('\n')
        f.write('<g id="0020_1">\n')
        f.write('<metadata id="CorelCorpID_0Corel-Layer"/>\n')
        
        str = createCirclePath(0,0,25)
        f.write(str)
        str = createRectPath(0,0,25)
        f.write(str)
        
        # for cnt in cntExt:
        #     type = cnt[0]
        #     if type =='c':
        #         str = circleSvg(cnt[1], coff, object_disp, object_startX, mainContureTop)
        #         if (str is None)==False:
        #             f.write(str)
        #     if type == 'm':
        #         str = roundRectSvg(cnt[1], coff)
        #         f.write(str)
        #     if type == 'b':
        #         str = boxSvg(cnt[1], coff, object_disp, object_startX)
        #         f.write(str)
        f.write('\n</g>\n')
        f.write("</svg>")
    return

