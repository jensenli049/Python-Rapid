pip install --user --upgrade opencv-python numpy matplotlib imutils scipy

import cv2 as cv
import math
import numpy as np
import glob
import os
import imutils
from imutils import perspective
from math import dist

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
        areaE = cv.contourArea(e)

        # Ignore contours that are too small or too large
        if areaT > min_a and max_a > areaT:
            contours_t.append(t)
        if areaE > min_a and max_a > areaE:
            contours_e.append(e)

    return contours_t, contours_e

def find_centroids(contours):
    # instantiate two empty lists
    cX, cY = [], []
    for c in contours:
        # calculate moments for each contour
        M = cv.moments(c)
        # avoid divide by zero error
        if M["m00"] == 0:
            return 0, 0
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
        
        # calculate rotation angle
        angle = rect[-1]
        if angle > 45:
            angle = 90 - angle
        else:
            angle = -angle
        angles.append(int(angle))
        """
        result = img.copy()
        box = np.int0(box)
        cv.drawContours(result,[box],0,(0,0,255),2)
        cv.imshow("RESULT", result)
        cv.waitKey(0)
        cv.destroyAllWindows()
        """
    return angles

def midpoint(ptA, ptB): # used for calculating distances
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def calculate_dists(image, width, contours):
    # sort contours smallest to largest
    sorted_contours = sorted(contours, key=cv.contourArea, reverse=False)
    pixelsPerMetric = None
    
    for cnt in sorted_contours:
        result = image.copy()
        box = cv.minAreaRect(cnt)
        box = cv.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        
        # calculate dimensions of object
        (tl, tr, br, bl) = box # indicates corners of bounding box
        mtlr = midpoint(tl, tr)
        mblr = midpoint(bl, br)
        mtll = midpoint(tl, bl)
        mbrr = midpoint(tr, br)
        center = midpoint(mtlr,mblr)

        # compute the Euclidean distance between the midpoints
        dA = np.linalg.norm(np.array(mtlr)-np.array(mblr))
        dB = np.linalg.norm(np.array(mtll)-np.array(mbrr))

        # compute the size of the object using given metric
        if pixelsPerMetric is None:
            pixelsPerMetric = dB / width

        hght = dA / pixelsPerMetric
        wdth = dB / pixelsPerMetric

        cv.putText(image, "{:.2f}x{:.2f}in".format(hght, wdth), 
                    (int(center[0] - 35), int(center[1] - 10)), 
                    cv.FONT_HERSHEY_SIMPLEX, 0.35, (218, 198, 38), 1)
        """
        box = np.int0(box)
        cv.drawContours(result,[box],0,(0,0,255),2)
        cv.imshow("RESULT", result)
        cv.waitKey(0)
        cv.destroyAllWindows()
        """

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
        cv.putText(result, "{:.1f}deg".format(a), 
                    (int(x - 35), int(y + 10)), 
                    cv.FONT_HERSHEY_SIMPLEX, 0.35, (218, 198, 38), 1)
        # draw axes
        cv.line(result, (x, y), (x_axisX, x_axisY), (127,255,0), 2)
        cv.line(result, (x, y), (y_axisX, y_axisY), (255,255,224), 2)
    cv.imshow('Output Image', result)
    cv.waitKey(0)
    cv.destroyAllWindows()

def nothing(x): #dummy function for trackbar
    pass

def check_folder(folder_name): #makes new directory if it does not already exist
    path = os.path.join(os.getcwd(), folder_name)
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)

def clear_images(folder_name, image_start): #removes all specified images from folder
    path = os.path.join(os.getcwd(), folder_name)
    for fname in os.listdir(path):
        if fname.startswith(image_start):
            os.remove(os.path.join(path,fname))

def take_webcam_pics(num, folder_name):
    check_folder(folder_name)
    #clear_images(folder_name, "calibration_pic")
    
    webcamVideo = cv.VideoCapture(0)
    cv.namedWindow("webcam") # used to display camera feed
    
    print("press space to save an image")
    while num >= 1:
        ret, frame = webcamVideo.read()
        if not ret: # check if camera is working
            print("Camera off")
            break
            
        cv.imshow("feed", frame) # display camera feed
         
        k = cv.waitKey(1) & 0xFF #gets value of key pressed
        if k == 27: # esc key pressed
            print("Escape hit, closing...")
            break
        elif k == 32: # space key pressed
            image_path = os.path.join(os.getcwd(), folder_name, "calibration_pic_{}.jpg".format(num))
            cv.imwrite(image_path, frame)            
            print("saving image")
            num -= 1
    webcamVideo.release()
    cv.destroyAllWindows()      
        

def cam_cal(newpics = False): # determine if new cals are needed
    # Defining the dimensions of checkerboard
    CHECKERBOARD = (7,10) # checkerboard needs to be large enough to load
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = [] 
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 

    # Defining the world coordinates for 3D points
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    if(newpics): #
        take_webcam_pics(3, "calibs")
    images = glob.glob('./calibs/*.jpg')
    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, 
            cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)
        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display them on the images of checker board
        """
        if ret == True:
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            #img = cv.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)

        #cv.imshow('img',img) # show images
        #cv.waitKey(0)

    cv.destroyAllWindows()

    h,w = img.shape[:2]

    """
    Performing camera calibration by passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    # print calibration values
    """
    print("Camera matrix : \n")
    print(mtx)
    print("dist : \n")
    print(dist)
    print("rvecs : \n")
    print(rvecs)
    print("tvecs : \n")
    print(tvecs)
    """
    return ret, mtx, dist, rvecs, tvecs # return calibration values for future images

def undistort_img(img, mtx, dist):
    #img = cv.imread(img)
    h, w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    
    # undistort
    dst = cv.undistort(img, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    #cv.imwrite('calibresult.png', dst)
    return dst

def find_bottom_contour(contours):
    sorted_contours = sorted(contours, key=lambda contours: cv.boundingRect(contours)[1], reverse=False) # sort left-to-right
    leftmost = []
    remainder = []
    for ind, cnt in enumerate(sorted_contours):
        if ind == 0:
            leftmost = cnt
        else:
            remainder.append(cnt)
    return leftmost, remainder
    
def draw_axes(imagedraw, origin, mtx, dist):
    CHECKERBOARD = (7,10)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:CHECKERBOARD[0],0:CHECKERBOARD[1]].T.reshape(-1,2)
    axis = np.float32([[10,0,0], [0,10,0], [0,0,-10]]).reshape(-1,3)
    
    img = cv.imread("./calibs/calibration_pic_1.jpg")
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)
    if ret == True:
        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Find the rotation and translation vectors.
        ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
        # project 3D points to image plane
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        
        # draw x,y,z axes from origin (leftmost centroid contour)
        imagedraw = cv.line(imagedraw, origin, tuple(imgpts[0].ravel()), (255,0,0), 5)
        imagedraw = cv.line(imagedraw, origin, tuple(imgpts[1].ravel()), (0,255,0), 5)
        imagedraw = cv.line(imagedraw, origin, tuple(imgpts[2].ravel()), (0,0,255), 5)

    return imagedraw

display_type = 0 # image: 0 | video: 1

ret, mtx, dist, rvecs, tvecs = cam_cal(False) # calibrate camera
print("Clearing active_pics")
clear_images(os.getcwd(), "active_pic") # clear old active pics
image_num = 1

cv.namedWindow('controls', cv.WINDOW_NORMAL)
cv.createTrackbar('Min Thresh','controls',0,255,nothing)
cv.createTrackbar('Max Thresh','controls',255,255,nothing)
cv.createTrackbar('Min Area','controls',2000,10000,nothing)
cv.createTrackbar('Max Area','controls',1000000,200000,nothing)

webcamVideo = cv.VideoCapture(0)

print("press space to save an image")
while True:
    if display_type == 1: # webcam active capture
        ret, frame = webcamVideo.read()
        undist_frame = undistort_img(frame, mtx, dist) # apply camera calibration
        imgcopy = undist_frame.copy()
        if not ret: # check if camera is working
            print("Camera off")
            break
    if display_type == 0: # static image capture
        #img = cv.imread("input1.jpg")
        img = cv.imread("input2.png")
        img = cv.resize(img, (int(img.shape[1]*0.6), int(img.shape[0]*0.6)), cv.INTER_AREA)
        #cntrs_t, cntrs_e = find_contours_auto(img) # auto-generated contours values --> will be changed
        imgcopy = img.copy()
        
    # get Trackbar values
    min_thres = int(cv.getTrackbarPos('Min Thresh','controls'))
    max_thres = int(cv.getTrackbarPos('Max Thresh','controls'))
    area_min = int(cv.getTrackbarPos('Min Area','controls'))
    area_max = int(cv.getTrackbarPos('Max Area','controls'))
    
    # calculate contours
    cntrs_t, cntrs_e = find_contours_man(imgcopy, min_thres, max_thres, area_min, area_max)
    leftmost, cntrs_t = find_bottom_contour(cntrs_t) # pops left most contour from list for axes
    _, cntrs_e = find_bottom_contour(cntrs_e) # shorten cntrs_e as well
    draw_contours(imgcopy, cntrs_t)
        
    #cv.imshow("orig_feed", frame) # display camera feed
    imgcopy = draw_axes(imgcopy, tuple(find_centroids(leftmost)), mtx, dist) # draw axes using leftmost contour and calibration plane
    cv.imshow("undist_feed", imgcopy) # display undistorted camera feed
    
    k = cv.waitKey(1) & 0xFF #gets value of key pressed
    if k == 27: # esc key pressed
        print("Escape hit, closing...")
        break
    elif k == 32: # space key pressed
        image_path = os.path.join(os.getcwd(), "active_pic_{}.jpg".format(image_num))
        cv.imwrite(image_path, imgcopy)
        print("saving image: active_pic_{}.jpg".format(image_num))
        image_num += 1
webcamVideo.release()
cv.destroyAllWindows()      

x_coords, y_coords = find_centroids(cntrs_t)
angs = calculate_orientation(cntrs_e)
calculate_dists(imgcopy, 1, cntrs_e)
draw_features(imgcopy, cntrs_t, angs, x_coords, y_coords)