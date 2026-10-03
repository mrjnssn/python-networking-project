import socket
import threading
from protocol import send_message, receive_message

def handle_client(connection, address):
    try:
        while True:
            message = receive_message(connection)

            if message is None:
                break

            print(message)
    finally:
        connection.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(("127.0.0.1", 5000))
sock.listen()

print("Waiting for a connection...")

while True:
    connection, address = sock.accept()

    # create a thread object
    receive_thread = threading.Thread(
        target=handle_client,
        args=(connection, address,)
    )

    receive_thread.start()

    print(receive_thread)


while True:
    payload = input("Message: ")

    if payload == "/quit":
        break
    
    send_message(connection, payload)

connection.close()






