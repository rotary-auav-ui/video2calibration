#!/usr/bin/env python

import cv2
import os
import argparse

def resize_or_crop(frame, desired_width, desired_height):
    """
    Adjusts the input frame by resizing it if the aspect ratio matches,
    or cropping it if the aspect ratio needs adjustment.

    Parameters:
        frame (numpy.ndarray): The input image or video frame.
        desired_width (int): The width of the adjusted frame.
        desired_height (int): The height of the adjusted frame.

    Returns:
        numpy.ndarray: The resized or cropped frame.
    """
    if desired_width is None or desired_height is None:
        return frame

    original_height, original_width = frame.shape[:2]
    desired_aspect = desired_width / desired_height
    original_aspect = original_width / original_height

    if abs(original_aspect - desired_aspect) < 0.01:
        # Aspect ratio is close enough, resize directly
        return cv2.resize(frame, (desired_width, desired_height))
    else:
        # Aspect ratio mismatch, crop to fit
        if original_aspect > desired_aspect:
            # Original is wider, crop horizontally
            new_width = int(original_height * desired_aspect)
            crop_start = (original_width - new_width) // 2
            frame = frame[:, crop_start:crop_start + new_width]
        else:
            # Original is taller, crop vertically
            new_height = int(original_width / desired_aspect)
            crop_start = (original_height - new_height) // 2
            frame = frame[crop_start:crop_start + new_height, :]

        return cv2.resize(frame, (desired_width, desired_height))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate picture for camera calibration.')
    parser.add_argument('-s', '--source', help='Camera source address', default=0, type=int)
    parser.add_argument('-wp', '--width', help='Width of picture taken', default=None, type=int)
    parser.add_argument('-hp', '--height', help='Height of picture taken', default=None, type=int)
    args = parser.parse_args()

    cam = cv2.VideoCapture(args.source)

    cur_path = os.getcwd()  # Current Path
    folder_dir = "output_picture"
    calib_imgs_dir = os.path.join(cur_path, folder_dir)

    print("Press SPACE key to take a picture, press ESC to close the script")
    if os.path.isdir(calib_imgs_dir):
        print(f"Folder exists!, writing to {folder_dir} directory") 
    else:
        print(f"Directory {folder_dir} not found, Creating directory")
        os.mkdir(calib_imgs_dir)

    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = resize_or_crop(frame, args.width, args.height)

        cv2.imshow("Image", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = f"calib_{img_counter}.png"
            cv2.imwrite(os.path.join(calib_imgs_dir, img_name), frame)
            print(f"{img_name} written!")
            img_counter += 1

    cam.release()
    cv2.destroyAllWindows()