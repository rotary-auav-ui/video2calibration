#!/usr/bin/env python
import argparse
import os
import pickle
from glob import glob

import cv2
import numpy as np
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calibrate camera using a video of a chessboard or a sequence of images.')
    parser.add_argument('input', help='input video file or glob mask')
    parser.add_argument('out', help='output calibration yaml file')
    parser.add_argument('--debug-dir', help='path to directory where images with detected chessboard will be written',
                        default=None)
    parser.add_argument('-c', '--corners', help='output corners file', default=None)
    parser.add_argument('-ph', '--pattern_height', help='pattern height', default=9, type=int)
    parser.add_argument('-pw', '--pattern_width', help='pattern width', default=6, type=int)
    parser.add_argument('-fs', '--framestep', help='use every nth frame in the video', default=20, type=int)
    parser.add_argument('-max', '--max-frames', help='limit the number of frames used for calibration', default=None, type=int)
    # parser.add_argument('--figure', help='saved visualization name', default=None)
    args = parser.parse_args()

    if os.path.isdir(args.input):  # Check if input is a folder
        # Get a sorted list of images in the folder
        source = sorted(glob(os.path.join(args.input, "*.jpg")) + glob(os.path.join(args.input, "*.png")))
    elif os.path.isfile(args.input):  # Check if input is a file
        # Assume the file is a video
        source = cv2.VideoCapture(args.input)
    else:
        raise ValueError("The input path is neither a valid folder nor a valid video file.")
    # square_size = float(args.get('--square_size', 1.0))

    pattern_size = (args.pattern_width, args.pattern_height)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    # pattern_points *= square_size

    obj_points = []
    img_points = []
    h, w = 0, 0
    frame = -1
    used_frames = 0
    while True:
        if isinstance(source, list):
            # Handling image list
            if frame >= len(source):  # Stop if all images are processed
                break
            img = cv2.imread(source[frame])
            frame += 1
        else:
            # Handling video capture
            retval, img = source.read()
            if not retval:  # Stop if no more frames in the video
                break
            frame += 1
            if frame % args.framestep != 0:  # Skip frames based on framestep
                continue

        print(f'Searching for chessboard in frame {frame}... ', end='')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img.shape[:2]
        found, corners = cv2.findChessboardCorners(img, pattern_size, flags=cv2.CALIB_CB_FILTER_QUADS)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
            used_frames += 1
            img_points.append(corners.reshape(1, -1, 2))
            obj_points.append(pattern_points.reshape(1, -1, 3))
            print('ok')
            if args.max_frames is not None and used_frames >= args.max_frames:
                print(f'Found {used_frames} frames with the chessboard.')
                break
        else:
            print('not found')

        if args.debug_dir:
            img_chess = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(img_chess, pattern_size, corners, found)
            cv2.imwrite(os.path.join(args.debug_dir, '%04d.png' % frame), img_chess)

    if args.corners:
        with open(args.corners, 'wb') as fw:
            pickle.dump(img_points, fw)
            pickle.dump(obj_points, fw)
            pickle.dump((w, h), fw)

# load corners
#    with open('corners.pkl', 'rb') as fr:
#        img_points = pickle.load(fr)
#        obj_points = pickle.load(fr)
#        w, h = pickle.load(fr)

    print('\ncalibrating...')
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)
    print("RMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: ", dist_coefs.ravel())

    if args.fisheye:
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.fisheye.calibrate(
            obj_points, img_points,
            (w, h), camera_matrix, np.array([0., 0., 0., 0.]),
            None, None,
            cv2.fisheye.CALIB_USE_INTRINSIC_GUESS, (3, 1, 1e-6))
        print("RMS:", rms)
        print("camera matrix:\n", camera_matrix)
        print("distortion coefficients: ", dist_coefs.ravel())

    calibration = {'rms': rms, 'camera_matrix': camera_matrix.tolist(), 'dist_coefs': dist_coefs.tolist()}
    with open(args.out, 'w') as fw:
        yaml.dump(calibration, fw)
