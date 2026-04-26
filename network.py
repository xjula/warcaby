import socket

# network.py
import socket


class Network:
    def __init__(self, host="127.0.0.1"):  # Dodany parametr host
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = 5555
        self.player_id = None

        # Próbujemy się połączyć
        res = self.connect()
        if res:
            self.player_id = int(res)

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            return self.client.recv(2048).decode()
        except:
            return None  # Zwracamy None zamiast pass dla łatwiejszej kontroli

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