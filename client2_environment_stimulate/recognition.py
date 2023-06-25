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


class Test:
    def __init__(self):
        self.number_of_correct = 0
        self.total_test_samples = 0

    def input(self):
        f = open("ref_name.pkl", "rb")
        self.ref_dictt = pickle.load(
            f
        )  # ref_dict=ref vs name //dictionary contain name of user with id as key
        f.close()

        f = open("ref_embed.pkl", "rb")
        self.embed_dictt = pickle.load(f)  # embed_dict- ref  vs embedding
        f.close()

        self.known_face_encodings = []  # encodingd of faces
        self.known_face_names = []  # ref_id of faces

        for ref_id, embed_list in self.embed_dictt.items():
            for embed in embed_list:
                self.known_face_encodings += [embed]
                self.known_face_names += [ref_id]

    def process_image(self, path):
        # print(path)
        frame = cv2.imread(path)
        if frame is None:
            return
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding
            )
            name = "Unknown"
            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding
            )
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                # name_in_path = path.split("/")[-1].split("_")[0]
                print(self.ref_dictt[name])
                if self.ref_dictt[name] in path.split("/")[-1]:
                    print(
                        f"{self.ref_dictt[name]}: {path.split('/')[-1].split('_')[0]}"
                    )
                    self.number_of_correct += 1

            # face_names.append(name)
        print(f"Process completed!! {path}")

    def train_main(self):
        # find the path of the folder train_dataset
        folder_path = "../test_dataset"
        # loop through every png image in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                print(f"******** Start processing image {file} ********")
                self.input()
                self.process_image(f"{folder_path}/{file}")
                self.total_test_samples += 1

        print("Trainning Complete")

    def evaluate(self):
        print(self.number_of_correct)
        accuracy = self.number_of_correct / self.total_test_samples
        return accuracy


if __name__ == "__main__":
    train = Test()
    train.train_main()

    accuracy = train.evaluate()
    print(f"Accuracy: {accuracy}")
