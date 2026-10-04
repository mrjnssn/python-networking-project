import socket
import threading
from protocol import send_message, receive_message

def handle_client(connection, address, clients, clients_lock):
    try:
        username = receive_message(connection)

        if username is None:
            return

        with clients_lock:
            clients[connection] = username

        while True:
            message = receive_message(connection)

            if message is None:
                break

            print(message)
            broadcast(message, connection, clients, clients_lock)
    finally:
        remove_client(connection, clients, clients_lock)

def broadcast(message, sender, clients, clients_lock):
    with clients_lock:
        clients_snapshot = clients.copy()
        username = clients[sender]
    
    message = f"{username}: {message}"
    
    for client in clients_snapshot:
        if client == sender:
            continue
        try:
            send_message(client, message)
        except OSError:
            remove_client(client, clients, clients_lock)

def remove_client(connection, clients, clients_lock):
    with clients_lock:
        if connection in clients:
            del clients[connection]
    connection.close()



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(("127.0.0.1", 5000))
sock.listen()

clients = {}
clients_lock = threading.Lock()

print("Waiting for a connection...")

while True:
    connection, address = sock.accept()

    # create a thread object
    receive_thread = threading.Thread(
        target=handle_client,
        args=(connection, address, clients, clients_lock)
    )

    receive_thread.start()

    print(receive_thread)
    








