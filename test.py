import cv2
import numpy as np

# read image through command line 
im = cv2.imread("D:/Projects/InsiTech/botProject/Adminka/LecalaConverter/learnopencv-master/BlobDetector/blob.jpg")

# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 10
params.maxThreshold = 200


# Filter by Area.
params.filterByArea = True
params.minArea = 1500

# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.87
    
# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.01

# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3 :
	detector = cv2.SimpleBlobDetector(params)
else : 
	detector = cv2.SimpleBlobDetector_create(params)


# Detect blobs.
keypoints = detector.detect(im)

# Draw detected blobs as red circles.
# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
# the size of the circle corresponds to the size of blob

im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Show blobs
cv2.imshow("Keypoints", im_with_keypoints)
cv2.waitKey(0)


# # convert the image to grayscale
# gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# # convert the grayscale image to binary image
# ret,thresh = cv2.threshold(gray_image,127,255,0)

# # find contour in the binary image
# contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
# for c in contours:
# 	# calculate moments for each contour
# 	M = cv2.moments(c)
# 	cX = int(M["m10"] / M["m00"])
# 	cY = int(M["m01"] / M["m00"])
	
	
#     # calculate x,y coordinate of center
# 	cv2.circle(img, (cX, cY), 5, (255, 255, 0), 5)
# 	cv2.putText(img, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
# 	# display the image
# 	cv2.imshow("Image", img)
# 	cv2.waitKey(0)