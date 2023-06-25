from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import pickle
import os

app = Flask(__name__)
# app.config["SECRET_KEY"] = "secret!"
MAX_BUFFER_SIZE = 50 * 1000 * 1000 * 1000
socketio = SocketIO(app, max_http_buffer_size=MAX_BUFFER_SIZE)


@socketio.on("connect")
def handle_connect(room):
    print(f"Client connected to {room}!!")
    emit("connect_response", "Client 1 connected !!")


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected")


@socketio.on("join")
def handle_join(data):
    print(f"Client join {data}")
    join_room(data)
    emit("response_join", f"Joined to room {data}")


@socketio.on("send_file_name")
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

    # Lastly emit this to the other client
    transfer_file_name = None
    with open("ref_name.pkl", "rb") as file:
        transfer_file_name = file.read()
    socketio.emit("broadcast_file_name", {"buffer": transfer_file_name})


@socketio.on("send_file_embed")
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
    # Lastly emit this to the other client
    transfer_file_embed = None
    with open("ref_embed.pkl", "rb") as file:
        transfer_file_embed = file.read()
    socketio.emit("broadcast_file_embed", {"buffer": transfer_file_embed})


if __name__ == "__main__":
    socketio.run(app)
