import socket
import threading
from protocol import receive_structured_message, send_structured_message


def receive_messages(sock):
    while True:
        message = receive_structured_message(sock)

        if message is None:
            return

        if not isinstance(message, dict):
            continue

        if message.get("type") != "CHAT":
            continue

        sender = message.get("sender")

        if not isinstance(sender, str) or not sender.strip():
            continue

        sender = sender.strip()

        payload = message.get("content")

        if not isinstance(payload, str) or not payload.strip():
            continue
        
        print(f"{sender}: {payload}")



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 5000))

username = ""
confirmation = ""

while username == "":
    username = input("Username: ")
    username = username.strip()

while True:
    confirmation = input(f"Do you want to enter the chat as {username}? Y/N\n> ")
    if confirmation.lower() == "n":
        username = ""
        while username == "":
            username = input("Enter new username: ")
            username = username.strip()
    elif confirmation.lower() == "y":
        message = {
            "type": "JOIN",
            "username": username
        }
        send_structured_message(sock, message)
        print("\nWelcome. Start messaging.")
        break
    else:
        print("Invalid input. Choose between (Y)es or (N)o.")

# create a thread object
receive_thread = threading.Thread(
    target=receive_messages,
    args=(sock,)
)

receive_thread.start()

while True:
    payload = input(" ")

    if payload == "/quit":
        break

    message = {
        "type": "CHAT",
        "content": payload
    }

    send_structured_message(sock, message)

sock.shutdown(socket.SHUT_RDWR)
receive_thread.join()
sock.close()