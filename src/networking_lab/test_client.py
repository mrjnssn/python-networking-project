import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 5000))


def send_message(sock, payload):
    payload_in_bytes = payload.encode('utf-8')
    header_size = 4 # de lengte van de header dwz het aantal bytes
    max_payload_size = int("9" * header_size) # de lengte van het bericht, dus dat is de header size x getallen 0 t/m 9

    if len(payload_in_bytes) > max_payload_size:
        raise ValueError("Message is too large")

    header = "0" * (header_size - len(str(len(payload_in_bytes)))) + str(len(payload_in_bytes))
    header_in_bytes = header.encode('utf-8')
    packet = header_in_bytes + payload_in_bytes

    sock.sendall(packet)

while True:
    payload = input("Message: ")

    if payload == "/quit":
        break

    send_message(sock, payload)

sock.close()