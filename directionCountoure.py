import enum
import os
import cv2
import numpy as np
import math
import drawsvg as drawSvg
from shapely import Point
from shapely import *
from shapely.geometry import Polygon
from shapely.ops import split
from mathUtils import *

class directionStatus(enum.Enum):
    undefined = 3

    halfCircleUp = 4
    halfCircleDown = 5
    sUpDown = 6
    sDownUp = 7
    cutoutTriangle = 8
    cutoutRect = 9
    cutoutCircle = 10

    camelA = 11
    camelB = 12
    camelC = 13
    camelD = 14
    def calcDirection(lineA, lineB):
        return directionStatus.undefined
    
class directionCountoure:
    def calcDirection(lineA, lineB):
        return directionStatus.undefined