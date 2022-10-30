#!/usr/bin/env python

import cv2
import os
import argparse

def crop_square(frame):
    height = frame.shape[0]
    width = frame.shape[1]
    if height < width:
        frame = frame[:, int(width/2) - int(height/2): int(width/2) + int(height/2)]
    else:
        frame = frame[int(height/2) - int(width/2):int(height/2) + int(height/2), :]
    return frame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate picture for camera calibration.')
    parser.add_argument('-s', '--source', help='Camera source address', default=0, type=int)
    parser.add_argument('-wp', '--width', help='Width of picture taken', default=200, type=int)
    parser.add_argument('-hp', '--height', help='Height of picture taken', default=200, type=int)
    args = parser.parse_args()
    
    cam = cv2.VideoCapture(args.source)

    cur_path = os.getcwd()  # Current Path
    folder_dir = "output_picture"
    calib_imgs_dir = os.path.join(cur_path, folder_dir)
    img_size = (args.width, args.height)          # Img Size

    print("Press SPACE key to take a picture, press ESC to close the script")
    if os.path.isdir(calib_imgs_dir):
        print(f"Folder exists!, writing to {folder_dir} directory") 
    else:
        print(f"Directory {folder_dir} not found, Creating directory")
        os.mkdir(calib_imgs_dir)
    
    img_counter = 0

    if args.width == args.height:
        square = True

    while True:
        ret, frame = cam.read()
        if square:
            frame = crop_square(frame)

        frame = cv2.resize(frame, img_size)
        if not ret:
            print("Failed to grab frame")
            break
        
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = f"calib_{img_counter}.png"
            cv2.imwrite(os.path.join(calib_imgs_dir, img_name), frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()

    cv2.destroyAllWindows()

