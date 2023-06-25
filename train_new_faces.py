import sys
import cv2
import os
import face_recognition
import pickle
import socketio

sio = socketio.Client()

# File transfer config
BUFFER_SIZE = 4096  # send 4096 bytes each time step
SEPARATOR = "<SEPARATOR>"


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
            for file in files:
                # Trainning
                personName = file.split("_")[1]
                personId = file.split("_")[0]
                # //assign var
                self.input(personName, personId)

                self.process_image(f"{folder_path}/{file}")

                f = open("ref_embed.pkl", "wb")
                pickle.dump(self.embed_dictt, f)
                f.close()
                print("Trainning Complete")


# **************** Handshake ****************
@sio.event
def connect():
    print("Connected to server!")


@sio.on("connect_response")
def on_my_response(data):
    print(f"Data my response, {data}")


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


if __name__ == "__main__":
    train = Train()
    train.train_main()

    sio.connect("http://127.0.0.1:5000")
    sio.emit("join", "room-1")

    transfer_file_name = None
    transfer_file_embed = None
    with open("ref_name.pkl", "rb") as file:
        transfer_file_name = file.read()
    with open("ref_embed.pkl", "rb") as file:
        transfer_file_embed = file.read()
    sio.emit("send_file_name", {"buffer": transfer_file_name})
    sio.emit("send_file_embed", {"buffer": transfer_file_embed})
