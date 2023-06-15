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


class mathSvg:
    def testSequence(diffs):
        all = len(diffs)
        if all < 4:
            return None
        # if all != 8:
            # return None
        result = []
        counter = 1
        deltaPrev = diffs[0][1]
        for index in range(1, all-1):
            delta = diffs[index][1]
            if np.sign(delta) == np.sign(deltaPrev):
                counter+=1
            else:
                result.append(counter)
                counter =1
            deltaPrev = delta
            
        if counter> 0:
            result.append(counter+1)
        return result
    def delta(diffs, index):
        val0=diffs[index]
        val1=diffs[index+1]
        delta = val1[1]-val0[1]
        return delta
    def isHalfCircle(seq):
        if seq is None:
            return False
        for index in range(len(seq)-1):
            if seq[index] > 2:
                if seq[index] == seq[index+1] or seq[index]-1 == seq[index+1] or seq[index] == seq[index+1]-1:
                    return True
        return False
    def doSignSeq(diffs):
        result = []
        for index in range(1, len(diffs)):
            if abs(diffs[index-1][1]) > abs(diffs[index][1]):
                result.append(True) 
            else:
                result.append(False) 
        return result
    def isCamelFigure(seq, diffs,countor):
        seq = mathSvg.doSignSeq(diffs)
        all= len(seq)
        if all == 7 and seq[0]==False and seq[1]==False and seq[2]==True and seq[3]==True and seq[4]==False and seq[5]==True and seq[6]==False:
            return 0
        if all == 7 and seq[0]==True and seq[1]==False and seq[2]==False and seq[3]==True and seq[4]==True and seq[5]==False and seq[6]==True:
            return 3
        if all == 9 and seq[0]==True and seq[1]==False and seq[2]==True and seq[3]==True and seq[4]==False and seq[5]==False and seq[6]==True and seq[7]==True:
            return 1
        if all == 8 and seq[0]==False and seq[1]==False and seq[2]==True and seq[3]==False and seq[4]==True and seq[5]==False and seq[6]==False and seq[7]==True:
            return 2
        return -1
    def isSFigure(seq, diffs,countor):
        # if seq is None:
        #     return 0
        # all = len(seq)
        result = []
        for index in range(1, len(diffs)):
            if abs(diffs[index-1][1]) > abs(diffs[index][1]):
                result.append(True) 
            else:
                result.append(False) 
        plus=0
        minus=0
        for diff in diffs:
            if np.sign(diff[1])>0:
                plus+=1
            else:
                minus+=1
        seqTF = mathSvg.isTrueFalseSeq(result)
        if seqTF: 
            if plus > minus:
                return 1
            else:
                return -1
        return 0
    def isTrueFalseSeq(seq):
        if len(seq)<2:
            return False
        truePresent = seq[0]
        if truePresent == False:
            return False
        falsePresent = False
        for ss in seq:
            if falsePresent == True:
                if ss == True: 
                    return False
            if ss == False: 
                falsePresent = True
        if falsePresent:
            return True
        return False
    def isAngleCorner(countor,w,h,lineA,lineB):
        if w > 2 * h:
            if lineA[1][0] > lineB[0][0]:
                return 1
            else:
                return 0
        return -1
    
