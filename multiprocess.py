#!/usr/bin/env python3
import sys
import time
import cv2
# from kafka import KafkaProducer
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

from weakref import ref
import face_recognition
import cv2
import numpy as np
import time
import pickle
import requests
from concurrent.futures import ProcessPoolExecutor
import os 
import moment 
from itertools import repeat
topic = "distributed-streaming"

# def compress_image(frame):

#     # Convert frame to grayscale
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Compress frame with compress level of 50
#     _, compressed_frame = cv2.imencode('.jpg', gray_frame, [cv2.IMWRITE_JPEG_QUALITY, 10])

#     print("Compress Frame raw: ", compressed_frame)
    
#     return compressed_frame


# def multiprocess_public_video():
    
#     # *********************Initialize************************
#     f=open("ref_name.pkl","rb")
#     ref_dictt=pickle.load(f)         #ref_dict=ref vs name //dictionary contain name of user with id as key
#     f.close()

#     f=open("ref_embed.pkl","rb")
#     embed_dictt=pickle.load(f) #embed_dict- ref  vs embedding 
#     f.close()

#     known_face_encodings = []  #encodingd of faces
#     known_face_names = []	   #ref_id of faces
#     #############################################################frame capturing from camera and face recognition
#     face_locations = []
#     face_encodings = []
#     face_names = []
#     process_this_frame = True

#     for ref_id , embed_list in embed_dictt.items():
#         for embed in embed_list:
#             known_face_encodings +=[embed]
#             known_face_names += [ref_id]

#     # *********************Initialize************************
#     producer = KafkaProducer(bootstrap_servers='localhost:9092')

#     nameFlag = ""
#     # video = {}

#     # if len(sys.argv) > 0 and len(sys.argv) > video_num:
#         # video_file = sys.argv[video_num]
#         # video = cv2.VideoCapture(video_file)

#     video_file = sys.argv[1]
#     # video_file2 = sys.argv[2]
#     # video_file3 = sys.argv[3]

#     # if video_num == 1:
#     video = cv2.VideoCapture(video_file)
#     # elif video_num == 2:
#     #     video = cv2.VideoCapture(video_file2)
#     # else: 
#     #     video = cv2.VideoCapture(video_file3)

#     while(video.isOpened()):
#         success, frame = video.read()

#         # Ensure file was read successfull
#         if not success:
#             print("bad read!")
#             break

#         # Grab a single frame of video
#         # ret, frame = video_capture.read()
#         # Resize frame of video to 1/4 size for faster face recognition processing
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#         # rgb_small_frame = small_frame[:, :, ::-1]
#         rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        
#         obj = recognition(ref_dictt, frame, rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)

#         newName = obj["data"]
#         newFrame = obj["frame"] #Frame đã process (compress, grayscale)
#         # print("newFrame byte raw: ", newFrame)
#         # Convert image to png
#         # ret, buffer = cv2.imencode('.jpg', frame)

#         send_obj = {}
#         # if  newName != nameFlag and newName != "":
#         #     send_obj = {
#         #         "frame": newFrame.tobytes(),
#         #         "id": newName,
#         #     }
#         # else:
#         #     send_obj = {
#         #         "frame": newFrame.tobytes(),
#         #         "id": "None",
#         #     }
#         nameFlag = newName
#         print("Video dang chay!!!!")
#         # Convert to bytes and send to kafka
#         # if video_num == 1:
#         # producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL)) #, partition=0)
#         producer.send(topic, newFrame.tobytes(), partition=0)
#         # elif video_num == 2:
#         #     producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL), partition=1)
#         # else:
#         #     producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL), partition=2)
#         time.sleep(0.2)
#     video.release()
#     return "name"


# def recognition(ref_dictt, frame, rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names):
#     # Only process every other frame of video to save time
#     if process_this_frame:
#         face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
#         for face_encoding in face_encodings:
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             best_match_index = np.argmin(face_distances)
#             if matches[best_match_index]:
#                 name = known_face_names[best_match_index] # name variable is the id of the user
#                 # ****Call API to update the enter/leave time*********************
#                 if nameFlag != name: # Compare the id of this frame with the prev frame to determin whether is it nessary to call the API
#                     nameFlag = name
#                     res = requests.post("http://localhost:3002/api/timestamp/{}".format(name), data={"enterTime": moment.now().format("YYYY/MM/DD HH:mm:ss"), "leaveTime": None})
#                 # ****************************************************************
#                 face_names.append(name)
#     process_this_frame = not process_this_frame


#     for (top, right, bottom, left), name in zip(face_locations, face_names):
#         # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#         top *= 4
#         right *= 4
#         bottom *= 4
#         left *= 4
#         frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#         # Draw a label with a name below the face
#         frame = cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         # if name != "Unknown":
#         frame = cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#         # else:
#             # frame = cv2.putText(frame, "Unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#         # frame = cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
#     compressed_frame = compress_image(frame)

#     return {"data": nameFlag, "frame": compressed_frame}


# def publish_video():
#     print('publishing video...')
#     multiprocess_public_video()
#     # with ProcessPoolExecutor(max_workers=2) as executor:
#     #     for name in executor.map(multiprocess_public_video):
#             # print(name)
        
#     print('publish complete')


# if __name__ == '__main__':
#     publish_video()

class MyProducer:
    # def __init__(self): 

    def draw_ident_box(self, face_locations, face_names, frame, ref_dictt):
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            frame = cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            # if name != "Unknown":
            frame = cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # else:
                # frame = cv2.putText(frame, "Unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # frame = cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        return frame
    
    def compress_image(self, frame):
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compress frame with compress level of 50
        _, compressed_frame = cv2.imencode('.jpg', gray_frame, [cv2.IMWRITE_JPEG_QUALITY, 5])

        print("Compress Frame raw: ", compressed_frame)
        
        return compressed_frame

    def recognition(self, ref_dictt, frame, rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names):
        # Only process every other frame of video to save time
        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index] # name variable is the id of the user
                    # ****Call API to update the enter/leave time*********************
                    if nameFlag != name: # Compare the id of this frame with the prev frame to determin whether is it nessary to call the API
                        nameFlag = name
                        res = requests.post("http://localhost:3002/api/timestamp/{}".format(name), data={"enterTime": moment.now().format("YYYY/MM/DD HH:mm:ss"), "leaveTime": None})
                    # ****************************************************************
                    face_names.append(name)
        process_this_frame = not process_this_frame

        frame = self.draw_ident_box(face_locations, face_names, frame, ref_dictt)

        compressed_frame = self.compress_image(frame)

        return (nameFlag, compressed_frame) #{"data": nameFlag, "frame": compressed_frame}

    def multiprocess_public_video(self):
        # *********************Initialize************************
        f=open("ref_name.pkl","rb")
        ref_dictt=pickle.load(f)         #ref_dict=ref vs name //dictionary contain name of user with id as key
        f.close()

        f=open("ref_embed.pkl","rb")
        embed_dictt=pickle.load(f) #embed_dict- ref  vs embedding 
        f.close()

        known_face_encodings = []  #encodingd of faces
        known_face_names = []	   #ref_id of faces
        #############################################################frame capturing from camera and face recognition
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        for ref_id , embed_list in embed_dictt.items():
            for embed in embed_list:
                known_face_encodings +=[embed]
                known_face_names += [ref_id]

        # *********************Initialize************************
        config_parser = ConfigParser()

        config_parser.read(os.path.join(os.path.dirname(__file__), 'getting_started.ini'))
        # print("Path: {}".format(config_parser['default']))
        config = dict(config_parser['default'])
        producer = Producer(config)

        nameFlag = ""
        # video = {}

        # if len(sys.argv) > 0 and len(sys.argv) > video_num:
            # video_file = sys.argv[video_num]
            # video = cv2.VideoCapture(video_file)

        video_file = sys.argv[1]
        # video_file2 = sys.argv[2]
        # video_file3 = sys.argv[3]

        # if video_num == 1:
        video = cv2.VideoCapture(video_file)
        # elif video_num == 2:
        #     video = cv2.VideoCapture(video_file2)
        # else: 
        #     video = cv2.VideoCapture(video_file3)

        while(video.isOpened()):
            success, frame = video.read()

            # Ensure file was read successfull
            if not success:
                print("bad read!")
                break

            # Grab a single frame of video
            # ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            # rgb_small_frame = small_frame[:, :, ::-1]
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
            
            #obj = self.recognition(ref_dictt, frame, rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)
            # nameFlag, compressed_frame = self.recognition(ref_dictt, frame, rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)
            
            # newName = obj["data"]
            # newFrame = obj["frame"] #Frame đã process (compress, grayscale)
            # print("newFrame byte raw: ", newFrame)
            # Convert image to png
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])

            # nameFlag = nameFlag
            print("Video dang chay!!!!")
            # Convert to bytes and send to kafka
            # if video_num == 1:
            # producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL)) #, partition=0)
            producer.produce(topic, buffer.tobytes())
            producer.poll(10)
            producer.flush()
            # elif video_num == 2:
            #     producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL), partition=1)
            # else:
            #     producer.send(topic, value=pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL), partition=2)
            time.sleep(0.2)
        video.release()
        return "name"

    def publish_video(self):
        print('publishing video...')
        self.multiprocess_public_video()
        print('publish complete')

if __name__ == "__main__":
    producer = MyProducer()
    producer.publish_video()