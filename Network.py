import socket
import pickle
from GongZhuEngine import *

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.237"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.game_info = self.connect()

    def get_game_info(self):
        return self.game_info
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            data = self.client.recv(2048)
            print(data)
            if data:
                if data != "get":
                    data = GongZhuEngine.deserialize(data)#is this the correct approach?
                return pickle.loads(data)
            else:
                print("No data received during connect")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None
    def send(self, data):
        try:
            if data != "get":
                    data = GongZhuEngine.deserialize(data)
            self.client.send(pickle.dumps(data.serialize()))
            response_data = self.client.recv(2048)
            if response_data:
                return GongZhuEngine.deserialize(pickle.loads(response_data))
            else:
                print("No data received during send")
                return None
        except socket.error as e:
            print(f"Socket error: {e}")
            return None
        except EOFError as e:
            print(f"EOFError: {e}")
            return None

   