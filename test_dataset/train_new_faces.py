import sys

# sys.path.append('/home/KLaHD/Downloads/face-recognition/lib/python3.6/site-packages')
import cv2
import os
import face_recognition
import pickle

# import requests
# import json


class Train:
    def input(self, personName, personId):
        self.name = personName
        self.ref_id = personId
        try:
            f = open("ref_name.pkl", "rb")
            self.ref_dictt = pickle.load(f)
            f.close()
        except:
            self.ref_dictt = {}
        self.ref_dictt[self.ref_id] = self.name
        f = open("ref_name.pkl", "wb")
        pickle.dump(self.ref_dictt, f)
        f.close()
        try:
            f = open("ref_embed.pkl", "rb")
            self.embed_dictt = pickle.load(f)
            f.close()
        except:
            self.embed_dictt = {}

    def process_image(self, path):
        print(path)
        frame = cv2.imread(path)
        if frame is None:
            return
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        if face_locations != []:
            listTemp = face_recognition.face_encodings(frame)
            if len(listTemp) == 0:
                print("Error", path)
                return
            # print(listTemp)
            face_encoding = listTemp[0]
            if self.ref_id in self.embed_dictt:
                self.embed_dictt[self.ref_id] += [face_encoding]
            else:
                self.embed_dictt[self.ref_id] = [face_encoding]
        print("Taken this image!!")

    def train_main(self):
        # find the path of the folder train_dataset
        folder_path = "train_dataset"
        # loop through every png image in the folder
        for root, dirs, files in os.walk(folder_path):
            for dir in dirs:
                personName = dir.split("-")[0]
                personId = dir.split("-")[1]

                # //assign var
                self.input(personName, personId)

                for imagesList in os.walk(f"{folder_path}/{dir}"):
                    for image in imagesList[2]:
                        self.process_image(f"{folder_path}/{dir}/{image}")
        f = open("ref_embed.pkl", "wb")
        pickle.dump(self.embed_dictt, f)
        f.close()
        print("Trainning Complete")


if __name__ == "__main__":
    train = Train()
    train.train_main()
