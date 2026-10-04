import socket
import threading
from protocol import send_message, receive_message


def receive_messages(sock):
    while True:
        message = receive_message(sock)

        if message is None:
            break

        print(f"\n{message}\n")


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
        send_message(sock, username)
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
    payload = input("> ")

    if payload == "/quit":
        break

    send_message(sock, payload)

sock.shutdown(socket.SHUT_RDWR)
receive_thread.join()
sock.close()