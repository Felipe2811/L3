import hashlib
import os
import socket
import threading
from concurrent.futures import thread

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (HOST, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MSG = "disc!"
CONNECT_MSG = "OK"
READY_MSG = "READY!"
LIMIT = 3
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
filename = "t8.shakespeare.txt"
filesize = os.path.getsize(filename)

def handle_client(conn, addr, barrier, hash):
    print(f"[NEW CONNECTION] {addr} connected.")
    msg = conn.recv(SIZE).decode(FORMAT)

    if msg == READY_MSG:
        # SEND Id of the client and OK
        id_client = str(threading.activeCount() - 1)
        msg = CONNECT_MSG
        conn.send(f"{msg}{SEPARATOR}{id_client}".encode(FORMAT))
        msg = conn.recv(SIZE).decode(FORMAT)
        print(f"[{addr}] {msg}")
        # WAIT all clients
        file = open(filename, "r")
        data = file.read()
        barrier.wait()
        # SEND filename and filesize
        conn.send(f"{filename}{SEPARATOR}{hash}".encode(FORMAT))
        # RECEIVE confirmation
        msg = conn.recv(SIZE).decode(FORMAT)
        print(f"[{addr}] {msg}")
        # SEND data
        conn.send(data.encode(FORMAT))
        msg = conn.recv(SIZE).decode(FORMAT)
        print(f"[{addr}] {msg}")
        file.close()
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

    else:
        print(f"[{addr}] {msg}")
        msg = f"Message received: {msg}"
        conn.send(msg.encode(FORMAT))

    conn.close()

def main():
    # Calculate the hash
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            md5.update(data)

    hash = md5.hexdigest()

    barrier = threading.Barrier(LIMIT)
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Client limit is {LIMIT}...")
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    
    while 1:
        conn, addr = server.accept()
        if (threading.activeCount() - 1) >= LIMIT :
            conn.close()
            print(f"[DENYING CONNECTION] Limit of clients reached!")
        else:
            thread = threading.Thread(target=handle_client, args=(conn, addr, barrier, hash))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
if __name__ == "__main__":
    main()
