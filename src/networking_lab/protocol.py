
import json

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

def send_message(sock, payload):
    payload_in_bytes = payload.encode('utf-8')
    max_payload_size = int("9" * HEADER_SIZE) # de lengte van het bericht, dus dat is de header size x getallen 0 t/m 9

    if len(payload_in_bytes) > max_payload_size:
        raise ValueError("Message is too large")

    header = "0" * (HEADER_SIZE - len(str(len(payload_in_bytes)))) + str(len(payload_in_bytes))
    header_in_bytes = header.encode('utf-8')
    packet = header_in_bytes + payload_in_bytes

    sock.sendall(packet)

def send_structured_message(sock, message):
    payload = json.dumps(message)
    send_message(sock, payload)

def receive_structured_message(sock):
    payload = receive_message(sock)

    if payload is None:
        return None

    payload_decoded = json.loads(payload)

    return payload_decoded