import socket
import threading
from protocol import send_message, receive_message


def receive_messages(sock):
    while True:
        message = receive_message(sock)

        if message is None:
            break

        print(message)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(("127.0.0.1", 5000))
sock.listen()

print("Waiting for a connection...")

connection, address = sock.accept()

# create a thread object
receive_thread = threading.Thread(
    target=receive_messages,
    args=(connection,)
)

receive_thread.start()

while True:
    payload = input("Message: ")

    if payload == "/quit":
        break
    
    send_message(connection, payload)

connection.close()






