from weakref import ref
import face_recognition
import cv2
import numpy as np
import glob
import time
import csv
import pickle
import requests
import json
import moment
import time
import pandas as pd
import os


def recognition(path):
    f = open("ref_name.pkl", "rb")
    ref_dictt = pickle.load(
        f
    )  # ref_dict=ref vs name //dictionary contain name of user with id as key
    f.close()

    f = open("ref_embed.pkl", "rb")
    embed_dictt = pickle.load(f)  # embed_dict- ref  vs embedding
    f.close()

    print("Ref_dict: ", ref_dictt)
    print("Embed_dict: ", embed_dictt)

    ############################################################################  encodings and ref_ids
    known_face_encodings = []  # encodingd of faces
    known_face_names = []  # ref_id of faces

    for ref_id, embed_list in embed_dictt.items():
        for embed in embed_list:
            known_face_encodings += [embed]
            known_face_names += [ref_id]

    #############################################################frame capturing from camera and face recognition
    video_capture = cv2.imread(path)
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    nameFlag = "Unknown"

    pTime = 0
    cTime = 0
    fpsList = {}

    # Grab a single frame of video
    pTime = cTime
    ret, frame = video_capture.read()
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding
            )
            name = "Unknown"
            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                # if nameFlag!=name:
                # 	print("Id", name)
                # 	res=requests.patch("http://localhost:5000/api/userInfo/{}".format(name), data={"id": name, "time": moment.now().format("YYYY/MM/DD HH:mm:ss")})
                # 	nameFlag=name
            face_names.append(name)
    process_this_frame = not process_this_frame
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        cv2.rectangle(
            frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
        )
        font = cv2.FONT_HERSHEY_DUPLEX
        if name != "Unknown":
            if ref_dictt[name] not in fpsList:
                fpsList.update({ref_dictt[name]: [int(fps)]})
                # fpsList[ref_dictt[name]] =
            else:
                fpsList.update({ref_dictt[name]: fpsList[ref_dictt[name]] + [int(fps)]})
            cv2.putText(
                frame,
                f"{int(fps)} - {ref_dictt[name]}",
                (left + 6, bottom - 6),
                font,
                1.0,
                (255, 255, 255),
                1,
            )
        else:
            cv2.putText(
                frame,
                "Unknown",
                (left + 6, bottom - 6),
                font,
                1.0,
                (255, 255, 255),
                1,
            )
    font = cv2.FONT_HERSHEY_DUPLEX


def train_main():
    # find the path of the folder train_dataset
    folder_path = "test_dataset"
    # loop through every png image in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            recognition(f"{folder_path}/{file}")

            personName = dir.split("-")[0]
            personId = dir.split("-")[1]

            # //assign var
            recognition(personName, personId)

            for imagesList in os.walk(f"{folder_path}/{dir}"):
                for image in imagesList[2]:
                    self.process_image(f"{folder_path}/{dir}/{image}")
    f = open("ref_embed_2.pkl", "wb")
    pickle.dump(self.embed_dictt, f)
    f.close()
    print("Trainning Complete")


if __name__ == "__main__":
    recognition()
