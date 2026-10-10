import socket
import threading
import argparse
from .protocol import receive_structured_message, send_structured_message

def handle_client(connection, connections, connections_lock, address, clients, clients_lock, shutdown_event):
    try:
        connection.settimeout(15)
        message = receive_structured_message(connection)

        if not isinstance(message, dict):
            return

        if message.get("type") != "JOIN":
            return

        username = message.get("username")

        if not isinstance(username, str) or not username.strip():
            return

        username = username.strip()

        with clients_lock:
            clients[connection] = username
        
        connection.settimeout(None)

        while True:
            message = receive_structured_message(connection)

            if not isinstance(message, dict):
                break

            message_type = message.get("type")

            if message_type == "CHAT":
                payload = message.get("content")

                if not isinstance(payload, str):
                    continue

                print(payload)
                broadcast(payload, connection, clients, clients_lock)
            elif message_type == "LIST_USERS":
                send_user_list(connection, clients, clients_lock)
    except socket.timeout:
        print(f"Client {address} timed out during JOIN handshake.")
    except OSError:
        if not shutdown_event.is_set():
            print(f"Connection error with {address}: {error}")
    finally:
        remove_client(connection, clients, clients_lock)

        with connections_lock:
            connections.discard(connection)

def broadcast(message, sender, clients, clients_lock):
    with clients_lock:
        clients_snapshot = clients.copy()
    
    username = clients_snapshot.get(sender)

    if username is None:
        return

    message = {
        "type": "CHAT",
        "sender": username,
        "content":  message
    }
    
    for client in clients_snapshot:
        if client == sender:
            continue
        try:
            send_structured_message(client, message)
        except OSError:
            remove_client(client, clients, clients_lock)

def remove_client(connection, clients, clients_lock):
    with clients_lock:
        if connection in clients:
            del clients[connection]
    connection.close()

def send_user_list(connection, clients, clients_lock):
    with clients_lock:
        usernames = list(clients.values())
    
    message = {
        "type": "USER_LIST",
        "users": usernames
    }

    send_structured_message(connection, message)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

parser = argparse.ArgumentParser(description="TCP chat server")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5000)

args = parser.parse_args()

sock.bind((args.host, args.port))
sock.listen()
print(f"Listening on {args.host}, port {args.port}")

connections = set()
connections_lock = threading.Lock()

clients = {}
clients_lock = threading.Lock()

client_threads = []

shutdown_event = threading.Event()

print("Waiting for a connection...")

try:
    while True:
        connection, address = sock.accept()

        with connections_lock:
            connections.add(connection)

        # create a thread object
        receive_thread = threading.Thread(
            target=handle_client,
            args=(connection, connections, connections_lock, 
            address, clients, clients_lock, shutdown_event)
        )

        receive_thread.start()
        client_threads.append(receive_thread)

        print(receive_thread)

except KeyboardInterrupt:
    print("\nServer shutting down...")
    shutdown_event.set()

finally:
    with connections_lock:
        connections_snapshot = list(connections)

    print(f"Closing {len(connections_snapshot)} active connection(s)...")

    for connection in connections_snapshot:
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            connection.close()
    
    for thread in client_threads:
        thread.join()

    sock.close()
    








