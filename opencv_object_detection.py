#!/usr/bin/env python
# coding: utf-8

# In[9]:


pip install --upgrade opencv-python numpy matplotlib


# In[1]:


# import opencv
import cv2 as cv
# import math functions
import math
import numpy as np
# import system libraries
import glob
import os


# In[2]:


def find_contours_auto(image):
    # convert image to grayscale
    imgray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # threshold image with otsu thresholding
    blur = cv.GaussianBlur(imgray,(5,5),0)
    ret,thr = cv.threshold(blur, 120, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    # find contours
    # tree = all contours
    contours_tree, hierarchy = cv.findContours(thr, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # external = only extreme outer contours (used for orientation)
    contours_ext, hierarchy = cv.findContours(thr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    contours_main = []
    for c in contours_tree:
        # Calculate the area of each contour
        area = cv.contourArea(c)

        # Ignore contours that are too small or too large
        if area > 2000 and 100000 > area:
            contours_main.append(c)
    """      
    result = image.copy()
    cv.drawContours(result, contours_main, -1, (0, 0, 255), 2)
    cv.imshow('Output Image', result)
    cv.waitKey(0)
    cv.destroyAllWindows()
    """
    return contours_main, contours_ext


# In[13]:


def find_contours_man(image, min_t, max_t, min_a, max_a):
    # convert image to grayscale
    imgray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # manual threshold
    blur = cv.GaussianBlur(imgray,(5,5),0)
    ret,thr = cv.threshold(blur, min_t, max_t, cv.THRESH_BINARY)
    # find contours
    # tree = all contours
    contours_tree, hierarchy = cv.findContours(thr, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # external = only extreme outer contours (used for orientation)
    contours_ext, hierarchy = cv.findContours(thr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    contours_t = []
    contours_e = []
    for t,e in zip(contours_tree, contours_ext):
        # Calculate the area of each contour
        areaT = cv.contourArea(t)
        areaE = cv.contourArea(t)

        # Ignore contours that are too small or too large
        if areaT > min_a and max_a > areaT:
            contours_t.append(t)
        if areaE > min_a and max_a > areaE:
            contours_e.append(e)

    return contours_t, contours_e


# In[4]:


def find_centroids(contours):
    # instantiate two empty lists
    cX, cY = [], []
    for c in contours:
        # calculate moments for each contour
        M = cv.moments(c)

        # calculate x,y coordinate of center
        cX.append(int(M["m10"] / M["m00"]))
        cY.append(int(M["m01"] / M["m00"]))
        """
        result = img.copy()
        cv.drawContours(result, contours, -1, (0, 0, 255), 2)
        cv.circle(img, (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])), 5, (0, 0, 0), -1)
        cv.imshow('Output Image', result)
        cv.waitKey(0)
        cv.destroyAllWindows()
        """
        
    return cX, cY


# In[5]:


def calculate_orientation(contours):
    # instantiate an empty list
    angles = []
    for c in contours:
        # calculate bounding box with minimum area, considers rotation
        rect = cv.minAreaRect(c)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        
        # calculate rotation angle
        angle = rect[-1]
        if angle > 45:
            angle = 90 - angle
        else:
            angle = -angle
        angles.append(int(angle))
        """
        result = img.copy()
        cv.drawContours(result,[box],0,(0,0,255),2)
        cv.imshow("RESULT", result)
        cv.waitKey(0)
        cv.destroyAllWindows()
        """
    return angles


# In[6]:


def draw_contours(image, contours):
    # draw contours
    for c in contours:
        cv.drawContours(image, contours, -1, (0, 0, 255), 2)
        
def draw_orientation(image, angles, cX, cY):
    for i, (a, x, y) in enumerate(zip(angles, cX, cY)):
        # draw centroid
        cv.circle(image, (x, y), 3, (0, 0, 0), -1)
        # calculate orientation axes
        hypotenuse = 100
        x_axisX = int(x+hypotenuse*math.cos(math.radians(a)))
        x_axisY = int(y-hypotenuse*math.sin(math.radians(a)))
        y_axisX = int(x-hypotenuse*math.sin(math.radians(a)))
        y_axisY = int(y-hypotenuse*math.cos(math.radians(a)))
        # draw axes
        cv.line(image, (x, y), (x_axisX, x_axisY), (127,255,0), 2)
        cv.line(image, (x, y), (y_axisX, y_axisY), (255,255,224), 2)

def draw_all(image, contours, angles, cX, cY):
    result =  image.copy()
    draw_contours(result, contours)
    draw_orientation(result, angles, cX, cY)
    cv.imshow('Output Image', result)
    cv.waitKey(0)
    cv.destroyAllWindows()

def draw_features(image, contours, angles, cX, cY):
    # Make a copy of the image to draw on
    result =  image.copy()
    for i, (c, a, x, y) in enumerate(zip(contours, angles, cX, cY)):
        # draw contours
        cv.drawContours(result, contours, -1, (0, 0, 255), 2)
        # draw centroid
        cv.circle(result, (x, y), 3, (0, 0, 0), -1)
        # calculate orientation axes (use complex numbers functions to simplify)
        hypotenuse = 100
        x_axisX = int(x+hypotenuse*math.cos(math.radians(a)))
        x_axisY = int(y-hypotenuse*math.sin(math.radians(a)))
        y_axisX = int(x-hypotenuse*math.sin(math.radians(a)))
        y_axisY = int(y-hypotenuse*math.cos(math.radians(a)))
        # draw axes
        cv.line(result, (x, y), (x_axisX, x_axisY), (127,255,0), 2)
        cv.line(result, (x, y), (y_axisX, y_axisY), (255,255,224), 2)
    cv.imshow('Output Image', result)
    cv.waitKey(0)
    cv.destroyAllWindows()


# In[7]:


def nothing(x): #dummy function for trackbar
    pass


# In[ ]:


# Defining the dimensions of checkerboard
CHECKERBOARD = (6,9)
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = []

# Defining the world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None

# Extracting path of individual image stored in a given directory
images = glob.glob('./cals/*.jpg')
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = true
    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)
    
    """
    If desired number of corner are detected,
    we refine the pixel coordinates and display 
    them on the images of checker board
    """
    if ret == True:
        objpoints.append(objp)
        # refining pixel coordinates for given 2d points.
        corners2 = cv.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
        
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
    
    cv.imshow('img',img)
    cv.waitKey(0)

cv.destroyAllWindows()

h,w = img.shape[:2]

"""
Performing camera calibration by 
passing the value of known 3D points (objpoints)
and corresponding pixel coordinates of the 
detected corners (imgpoints)
"""
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera matrix : \n")
print(mtx)
print("dist : \n")
print(dist)
print("rvecs : \n")
print(rvecs)
print("tvecs : \n")
print(tvecs)


# In[17]:


#img = cv.imread("input_img.jpg")
img = cv.imread("image2.png")
img = cv.resize(img, (int(img.shape[1]*0.6), int(img.shape[0]*0.6)), cv.INTER_AREA)
cntrs_t, cntrs_e = find_contours_auto(img) # auto-generated contours values --> will be changed

# create a seperate window named 'controls' for trackbar
cv.namedWindow('controls', cv.WINDOW_NORMAL)
# create trackbars in 'controls' window
cv.createTrackbar('Min Thresh','controls',0,255,nothing)
cv.createTrackbar('Max Thresh','controls',255,255,nothing)
cv.createTrackbar('Min Area','controls',2000,10000,nothing)
cv.createTrackbar('Max Area','controls',1000000,200000,nothing)

while(1):
    imgcopy = img.copy()
    
    min_thres = int(cv.getTrackbarPos('Min Thresh','controls'))
    max_thres = int(cv.getTrackbarPos('Max Thresh','controls'))
    area_min = int(cv.getTrackbarPos('Min Area','controls'))
    area_max = int(cv.getTrackbarPos('Max Area','controls'))
    
    cntrs_t, cntrs_e = find_contours_man(img, min_thres, max_thres, area_min, area_max)
    draw_contours(imgcopy, cntrs_t)

    cv.imshow('Contoured Image', imgcopy)

    # wait for the user to press escape and break the while loop 
    k = cv.waitKey(1) & 0xFF
    if k == 27: 
        break

# destroys all window
cv.destroyAllWindows()

x_coords, y_coords = find_centroids(cntrs_t)
angs = calculate_orientation(cntrs_e)
draw_features(img, cntrs_t, angs, x_coords, y_coords)


# In[ ]:




