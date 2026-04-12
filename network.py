import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "127.0.0.1"
        self.port = 5555
        self.player_id = int(self.connect())

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        """Wysyła dane (np. 'row1,col1:row2,col2') i odbiera odpowiedź."""
        try:
            self.client.send(str.encode(data))
        except socket.error as e:
            print(e)

    def receive(self):
        """Odbiera dane o ruchu przeciwnika (nieblokujące)."""
        try:
            self.client.setblocking(False)
            data = self.client.recv(2048).decode()
            if not data:
                return None
            return data
        except BlockingIOError:
            return None
        except Exception as e:
            return None

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass