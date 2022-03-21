pip install opencv-python numpy matplotlib

import cv2 as cv
import math
import numpy as np

def find_contours(image):
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
    
    contours_main  = []
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

img = cv.imread("image2.png")
 
if img is None:
  print("Error: File not found")
  exit(0)
 

cntrs_t, cntrs_e = find_contours(img)
x_coords, y_coords = find_centroids(cntrs_t)
angs = calculate_orientation(cntrs_e)
draw_features(img, cntrs_t, angs, x_coords, y_coords)