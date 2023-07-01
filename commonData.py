

# статус паралельных линий
import enum


class ParallStatus(enum.Enum):
    # не паралельны
    none = 0
    # закругленный угол
    vert = 1
    vert_left = 2
    vert_right = 3
    # последовательность линий
    hor_down = 4
    hor_up = 5
    hor = 6
    def isCoord(stat):
        if stat == ParallStatus.none:
            return False
        if stat == ParallStatus.vert or stat == ParallStatus.vert_left or stat == ParallStatus.vert_right:
            return False
        if stat == ParallStatus.hor_down or stat == ParallStatus.hor_up or stat == ParallStatus.hor:
            return False
        return True

class LineStatus(enum.Enum):
    round = 0
    sequest = 1
    parallel = 2
    undefined = 3

class Corner:
    cross = ParallStatus.none
    minX = minY =maxX =maxY=0
    linesFig = None
    pointsFig = None
    cornerFig = None
    dirFig = None
    def __init__(self, minX,minY,maxX,maxY,linesFig,cross, pointsFig):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.cross = cross
        self.linesFig = linesFig
        self.pointsFig = pointsFig
