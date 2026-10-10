import socket
import threading
import argparse
import queue
from .protocol import receive_structured_message, send_structured_message


def receive_messages(sock, stop_event):
    try:
        while True:
            message = receive_structured_message(sock)

            if message is None:
                if not stop_event.is_set():
                    print("\nServer disconnected.")
                return

            if not isinstance(message, dict):
                continue

            message_type = message.get("type")

            if message_type == "CHAT":
                sender = message.get("sender")

                if not isinstance(sender, str) or not sender.strip():
                    continue

                sender = sender.strip()

                payload = message.get("content")

                if not isinstance(payload, str) or not payload.strip():
                    continue
                
                print(f"{sender}: {payload}")
            elif message_type == "USER_LIST":
                usernames = message.get("users")

                if isinstance(usernames, list) and all(isinstance(username, str) and username.strip() for username in usernames):
                    print(f"Online users ({len(usernames)}):")

                    for username in usernames:
                        print(f"- {username}")
    
    except OSError:
        if not stop_event.is_set():
            print("\nConnection to server lost.")
    
    finally:
        stop_event.set()

def read_user_input(outgoing_queue, stop_event):
    while not stop_event.is_set():
        try:
            payload = input("")
        except EOFError:
            stop_event.set()
            return
        
        outgoing_queue.put(payload)

def main():
    parser = argparse.ArgumentParser(description="TCP chat client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)

    args = parser.parse_args()

    while True:
        username = input("Username: ").strip()
        
        if not username:
            print("Username cannot be empty.")
            continue
        
        confirmation = input(
            f"Do you want to enter the chat as {username}? Y/N\n> "
            ).strip().lower()
       
        if confirmation == "n":
            continue
        elif confirmation.lower() == "y":
            break
        else:
            print("Invalid input. Choose between (Y)es or (N)o.")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((args.host, args.port))
        send_structured_message(sock, {
            "type": "JOIN",
            "username": username
        })
    except OSError as error:
        print(f"Could not connect to or join the server: {error}")
        sock.close()
        return

    print("\nWelcome. Start messaging.")


    # create a thread object
    stop_event = threading.Event()
    outgoing_queue = queue.Queue()

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(sock, stop_event)
    )

    receive_thread.start()

    input_thread = threading.Thread(
        target=read_user_input,
        args=(outgoing_queue, stop_event),
        daemon=True
    )

    input_thread.start()

    while not stop_event.is_set():
        try:
            payload = outgoing_queue.get(timeout=0.2)
        except queue.Empty:
            continue
        
        if stop_event.is_set():
            break

        try:
            if payload == "/quit":
                break
            
            if payload == "/users":
                message = {
                    "type": "LIST_USERS",
                }
            else:
                message = {
                    "type": "CHAT",
                    "content": payload
                }

            send_structured_message(sock, message)
        except OSError:
            print("\nConnection to server lost.")
            stop_event.set()
            break

    stop_event.set()

    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    receive_thread.join()
    sock.close()

if __name__ == "__main__":
    main()