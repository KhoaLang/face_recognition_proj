import pickle
import socketio
import os

sio = socketio.Client()

# File transfer config
BUFFER_SIZE = 4096  # send 4096 bytes each time step
SEPARATOR = "<SEPARATOR>"


@sio.on("broadcast_file_name")
def on_send_file(buffer):
    # print("Name", buffer["buffer"])
    ref_dictt = {}
    try:
        f = open("ref_name.pkl", "rb")
        ref_dictt = pickle.load(f)
        # print(ref_dictt)
        f.close()
    except:
        ref_dictt = {}

    if not ref_dictt:
        f = open("ref_name.pkl", "wb")
        f.write(buffer["buffer"])
        f.close()
    else:
        # Load the buffer into dictionary
        f = open("temp_ref_name.pkl", "wb")
        f.write(buffer["buffer"])
        f.close()

        # Read current file and new file
        f = open("temp_ref_name.pkl", "rb")
        data = pickle.load(f)
        f.close()
        f2 = open("ref_name.pkl", "rb")
        curr_data = pickle.load(f2)
        f2.close()

        print(data)
        print(curr_data)

        newest_index = list(data)[-1]
        curr_data[newest_index] = data[newest_index]
        f = open("ref_name.pkl", "wb")
        pickle.dump(curr_data, f)
        f.close()

        os.remove("temp_ref_name.pkl")


@sio.on("broadcast_file_embed")
def on_send_file(buffer):
    ref_dictt = {}
    try:
        f = open("ref_embed.pkl", "rb")
        ref_dictt = pickle.load(f)
        # print(ref_dictt)
        f.close()
    except:
        ref_dictt = {}

    if not ref_dictt:
        f = open("ref_embed.pkl", "wb")
        f.write(buffer["buffer"])
        f.close()
    else:
        # Load the buffer into dictionary
        f = open("temp_ref_embed.pkl", "wb")
        f.write(buffer["buffer"])
        f.close()

        # Read current file and new file
        f = open("temp_ref_embed.pkl", "rb")
        data = pickle.load(f)
        f.close()
        f2 = open("ref_embed.pkl", "rb")
        curr_data = pickle.load(f2)
        f2.close()

        newest_index = list(data)[-1]
        curr_data[newest_index] = data[newest_index]
        f = open("ref_embed.pkl", "wb")
        pickle.dump(curr_data, f)
        f.close()

        os.remove("temp_ref_embed.pkl")


@sio.on("response_join")
def response_join(data):
    print(data)


if __name__ == "__main__":
    sio.connect("http://127.0.0.1:5000")
    sio.emit("join", "room-2")
