#!/usr/bin/env python3

import datetime
from flask import Flask, Response, jsonify
# from kafka import KafkaConsumer
# from kafka import TopicPartition
import json
import pickle
from weakref import ref
import face_recognition
import cv2
import numpy as np
from flask_cors import CORS
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import os



# Fire up the Kafka Consumer
topic = "distributed-streaming"

# consumers = []
# for i in range(0,3):
# consumer = Consumer(bootstrap_servers=['localhost:9092'])
# consumer.assign([TopicPartition(topic, 0)])
    # consumers.append(consumer)

# Set the consumer in a Flask App
app = Flask(__name__)
CORS(app)

@app.route('/video1', methods=['GET'])
def video1():
    return Response(
        get_video_stream(), #Trả về các Frame mà Flask đọc được 
        mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/video2', methods=['GET'])
# def video2():
#     return Response(
#         get_video_stream(1), #Trả về các Frame mà Flask đọc được 
#         mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/video3', methods=['GET'])
# def video3():
#     return Response(
#         get_video_stream(2), #Trả về các Frame mà Flask đọc được 
#         mimetype='multipart/x-mixed-replace; boundary=frame')

def get_video_stream():
    # consumer = None
    # for i in range(0,3):
    #     if video_num == i:
    #         consumer = consumers[i]

    config_parser = ConfigParser()
    config_parser.read(os.path.join(os.path.dirname(__file__), 'getting_started.ini'))
    config = dict(config_parser['default'])
    config.update(config_parser['consumer'])
    consumer = Consumer(config)
    consumer.subscribe([topic])

    # for msg in consumer.poll(1.0):
    #     print('Nhan duoc du lieu')
    #     # value=pickle.loads(msg.value)
    #     yield (b'--frame\r\n'
    #            b'Content-Type: image/jpg\r\n\r\n' + msg.value + b'\r\n\r\n') #msg.value là các Frame

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpg\r\n\r\n' + msg.value() + b'\r\n\r\n') #msg.value là các Frame
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()


if __name__ == "__main__":
# def main():
    app.run(host='0.0.0.0', debug=True)
