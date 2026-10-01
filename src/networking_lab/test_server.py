import socket
import threading

HEADER_SIZE = 4

def receive_exactly(connection, target_length):
    msg = b""

    while len(msg) < target_length:
        chunk = connection.recv(target_length - len(msg))

        if not chunk:
            if not msg:
                return b""
            
            raise ConnectionError("Connection closed before all bytes were received")

        msg += chunk
    
    return msg

def receive_message(sock):
    # receive header
    header_bytes = receive_exactly(sock, HEADER_SIZE)

    if not header_bytes:
        return None

    payload_size = int(header_bytes.decode("utf-8"))

    # receive paylaod
    payload_in_bytes = receive_exactly(sock, payload_size)
    payload = payload_in_bytes.decode("utf-8")

    return payload

def receive_messages(sock):
    while True:
        message = receive_message(sock)

        if message is None:
            break

        print(message)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(("127.0.0.1", 5000))
sock.listen()

print("Waiting for a connection...")

connection, address = sock.accept()

# create a thread object
receive_thread = threading.Thread(
    target=receive_messages,
    args=(sock,)
)

receive_thread.start()

while True:
    payload = input("Message: ")

    if payload == "/quit":
        break
    
    send_message(sock, payload)

sock.close()






