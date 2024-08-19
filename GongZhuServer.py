import socket
from _thread import *
import sys, signal
from GongZhuEngine import *
import pickle

server = "192.168.1.237"
#server = "10.21.179.143" Founders Hall (NYU) WiFi 

port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(4) #only 4 players
print("Server Started. Waiting for connection...")

engine = GongZhuEngine()

def threaded_client(conn):
    global engine
    conn.send(pickle.dumps(engine.serialize()))
    reply = ""
    while True:
        try: 
            data = pickle.loads(conn.recv(2048))
            reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                if isinstance(data, str) and data == "get":
                    print("Information gotten")
                    conn.sendall(pickle.dumps(engine.serialize()))
                else:
                    engine = GongZhuEngine.deserialize(data)
                    conn.sendall(pickle.dumps(engine.serialize()))
        except Exception as e:
            print(f"Error: {e}")
            break
    print("Lost Connection")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))

