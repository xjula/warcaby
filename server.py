import socket
import threading

# Konfiguracja serwera
HOST = '0.0.0.0' # Adres lokalny (do testów na jednym PC)
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(2)

clients = []

def handle_client(conn, player_id):
    conn.send(str.encode(str(player_id))) # Wysyłamy graczowi jego ID (1 lub 2)
    
    while True:
        try:
            data = conn.recv(2048).decode() # Odbieramy dane o ruchu
            if not data:
                break
            
            # Przesyłamy ruch do drugiego gracza
            for client in clients:
                if client != conn:
                    client.sendall(str.encode(data))
        except:
            break
    conn.close()

print("Serwer oczekuje na połączenia...")
while len(clients) < 2:
    conn, addr = server.accept()
    player_id = len(clients) + 1
    clients.append(conn)
    print(f"Gracz {player_id} połączony z {addr}")
    threading.Thread(target=handle_client, args=(conn, player_id)).start()