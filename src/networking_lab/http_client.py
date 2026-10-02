import socket
from protocol import receive_exactly

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
    
def receive_chunked_body(sock):
    body = b""

    while True:
        chunk = receive_until(sock, b"\r\n")
        size = int(chunk, 16)
        
        if size == 0:
            # consume trailers before returning body so that sock buffer is empty
            while True:
                trailer_line = receive_until(sock, b"\r\n")

                if not trailer_line:
                    return body
            
        chunk = receive_exactly(sock, size)
        body += chunk

        chunk_delimiter = receive_exactly(sock, len(b"\r\n"))

        if chunk_delimiter != b"\r\n":
            raise ValueError("HTTP framing is not valid.")




http_version, status_code, reason_phrase, headers = receive_headers(sock, b"\r\n")

print(f"HTTP version: {http_version}")
print(f"Status code:  {status_code}")
print(f"Reason:       {reason_phrase}")
print("\n")

if headers[b"Transfer-Encoding"] == b"chunked":
    body = receive_chunked_body(sock)

    print(body)
