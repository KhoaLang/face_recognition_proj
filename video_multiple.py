#!/usr/bin/env python3

import datetime
from flask import Flask, jsonify, make_response, Response
import time
import json
import pickle
from weakref import ref
import face_recognition
import cv2
import numpy as np
from flask_cors import CORS
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import os
from face_recog import Face_Recog
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue, Pipe
from multiprocessing import Process
import multiprocessing


app = Flask(__name__)
CORS(app)

# @app.route('/video', methods=['GET'])
# def video1():
#     return Response(process(param_string()[0]), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video2', methods=['GET'])
# def video2():
#     return Response(process(param_string()[1]), mimetype='multipart/x-mixed-replace; boundary=frame')   

@app.route('/video<int:Number>', methods=['GET'])
def video(Number):
    return Response(process(param_string()[Number-1]), mimetype='multipart/x-mixed-replace; boundary=frame')   


def process(video_string):
    cam = cv2.VideoCapture(video_string)
    face_recog = Face_Recog()
    parent_conn, child_conn = Pipe()
    q_input = Queue()
    q_output = Queue()
    while cam.isOpened():
        start_time = time.time()
        ret, frame = cam.read()
        if not ret: 
            print("bad read!")
            break
        p = Process(target=face_recog.publish_video, args=(frame, child_conn, start_time ))
        p.start()
        q_output.put(parent_conn.recv())
        p.join()
        if not q_output.empty():
            yield (b'--frame\r\n' b'Content-Type: image/jpg\r\n\r\n' + q_output.get() + b'\r\n\r\n')
        
def param_string():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', metavar='file', type=str, nargs='+', help='input MP4 files with .mp4 extension')
    args = parser.parse_args()
    print(args)
    video_string = args.input
    return video_string

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

