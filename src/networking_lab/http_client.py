import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = "example.com"
method = "GET"
http_version = "1.1"

sock.connect((address, 80))

request = f"{method} / HTTP/{http_version}\r\nHost: {address}\r\n\r\n"
request_in_bytes = request.encode("utf-8")

sock.sendall(request_in_bytes)

def receive_until(sock, delimiter):
    data = b""
    msg = b""

    while True:
        data = sock.recv(1)
        
        if not data:
            if not msg:
                return b""
            
            raise ConnectionError("Connection closed before delimiter was received.")

        msg += data

        if msg.endswith(delimiter):
            return msg[:-len(delimiter)]

def receive_headers(sock, delimiter):
    status_line = receive_until(sock, delimiter)

    http_version, status_code, reason_phrase = status_line.split(b" ", 2)

    headers = {}

    while True:
        header = receive_until(sock, delimiter)

        if not header:
            return http_version, status_code, reason_phrase, headers

        header_type, header_value = header.split(b": ", 1)

        headers[header_type] = header_value
    
    

http_version, status_code, reason_phrase, headers = receive_headers(sock, b"\r\n")

print(headers)