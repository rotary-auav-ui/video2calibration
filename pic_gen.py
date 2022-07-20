#!/usr/bin/env python

from importlib.resources import path
import cv2
import os

cam = cv2.VideoCapture(0)     # Change the number according to the camera that would be use!

calib_imgs_path= os.getcwd()  # Current Path
calib_imgs = "calib_imgs"     # Folder Name
calib_imgs_dir = os.path.join(calib_imgs_path,calib_imgs)
img_size = (200,200)          # Img Size

print("This is a script to take a picture with OpenCV, press SPACE key to take a picture, press Esc to close the script")
if os.path.isdir(calib_imgs_dir):
    print("Path Exists!, writing to calib_imgs directory") 
else:
    print("Directory isn't found, creating calib_imgs directory")
    os.mkdir(calib_imgs_dir)
img_counter = 0

while True:
    ret, frame = cam.read()
    frame = cv2.resize(frame, img_size)
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "img_calib_{}.png".format(img_counter)
        cv2.imwrite(os.path.join(calib_imgs_dir, img_name), frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()

