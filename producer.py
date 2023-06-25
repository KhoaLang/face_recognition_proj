import sys
import time
import cv2
from kafka import KafkaProducer
from weakref import ref
import face_recognition
import cv2
import numpy as np
import time
import pickle
import requests
import moment

topic = "distributed-streaming"




def recognition(rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names):
    # print("Ref_dict: ", ref_dictt)
    # print("Embed_dict: ", embed_dictt)
    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        # face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     tempName = known_face_names[first_match_index]
            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index] # name variable is the id of the user
                # print("Tới bước kiểm tra process_this_frame = True", process_this_frame)
                # print("Name đầu: ", type(name))
                # *****Call API to update the enter/leave time**********************
                if nameFlag != name: # Compare the id of this frame with the prev frame to determin whether is it nessary to call the API
                    print("Name thứ 2: ", name)
                    nameFlag=name
                    # print("Name thứ 2 + 1: ", nameFlag)
                    res = requests.post("http://localhost:3002/api/timestamp/{}".format(name), data={"enterTime": moment.now().format("YYYY/MM/DD HH:mm:ss"), "leaveTime": None})
                    # time.sleep(0.2)
                # ******************************************************************

            # face_names.append(name)
    process_this_frame = not process_this_frame
    return nameFlag

def publish_video(video_path1, ref_dictt, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names):
    """
    Publish given video file to a specified Kafka topic. 
    Kafka Server is expected to be running on the localhost. Not partitioned.
    
    :param video_file: path to video file <string>
    """
    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    # Open file
    video = cv2.VideoCapture(video_path1)
    
    print('publishing video...')

    while(video.isOpened()):
        success, frame = video.read()

        # Ensure file was read successfully
        if not success:
            print("bad read!")
            break

        nameFlag = "Unknown"
        # Grab a single frame of video
        # ret, frame = video_capture.read()
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # print("Trước khi gọi recog")
        nameFlag = recognition(rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)
        # print("Sau khi gọi recog")

        # Convert image to png
        ret, buffer = cv2.imencode('.jpg', frame)

        # Convert to bytes and send to kafka
        producer.send(topic, value=buffer.tobytes(), partition=0)

        time.sleep(0.2)
    video.release()
    print('publish complete')

    
def publish_camera(ref_dictt, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names):
    """
    Publish camera video stream to specified Kafka topic.
    Kafka Server is expected to be running on the localhost. Not partitioned.
    """

    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    camera = cv2.VideoCapture(0)
    nameFlag = "Unknown"
    try:
        while(True):
            success, frame = camera.read()

            # Grab a single frame of video
            # ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            # print("Trước khi gọi recog", nameFlag)
            newName = recognition(rgb_small_frame, nameFlag, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)
            nameFlag = newName
            print(nameFlag)
        
            ret, buffer = cv2.imencode('.jpg', frame)
            send_obj = {}
            if newName != "Unknown" and newName != nameFlag:
                send_obj = {
                    "frame": buffer.tobytes(),
                    "id": newName,
                    "name": ref_dictt[newName]
                }
            else:
                send_obj = {
                    "frame": buffer.tobytes(),
                    "id": "None",
                    "name": "None"
                }
            producer.send(topic, pickle.dumps(send_obj, protocol = pickle.DEFAULT_PROTOCOL), partition=0)
            # producer.send(topic, buffer.tobytes(), partition=0)
            
            # print("Loop before sleep")
            # print(nameFlag)
            # Choppier stream, reduced load on processor
            time.sleep(0.1)

    except:
        print("\nExiting.")
        sys.exit(1)

    
    camera.release()


if __name__ == '__main__':
    """
    Producer will publish to Kafka Server a video file given as a system arg. 
    Otherwise it will default by streaming webcam feed.
    """

    f=open("ref_name.pkl","rb")
    ref_dictt=pickle.load(f)         #ref_dict=ref vs name //dictionary contain name of user with id as key
    f.close()

    f=open("ref_embed.pkl","rb")
    embed_dictt=pickle.load(f)      #embed_dict- ref  vs embedding 
    f.close()

    known_face_encodings = []  #encodingd of faces
    known_face_names = []	   #ref_id of faces
    #############################################################frame capturing from camera and face recognition
    # video_capture = cv2.VideoCapture(0)  ***
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True



    for ref_id , embed_list in embed_dictt.items():
        for embed in embed_list:
            known_face_encodings +=[embed]
            known_face_names += [ref_id]

    if(len(sys.argv) > 1):
        video_path = sys.argv[1]
        publish_video(video_path1, ref_dictt, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)
    else:
        print("publishing feed!")
        publish_camera(ref_dictt, known_face_names, known_face_encodings, process_this_frame, face_locations, face_encodings, face_names)

