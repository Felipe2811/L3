from concurrent.futures import thread
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "disc!"
CONNECT_MSG = "OK"
READY_MSG = "READY!"
LIMIT = 2
barrier = threading.Barrier(LIMIT)

def handle_client(conn, addr, barrier):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    msg = conn.recv(SIZE).decode(FORMAT)

    if msg == READY_MSG:
        connected = True
        msg = CONNECT_MSG
        conn.send(msg.encode(FORMAT))
        while connected:
            msg = conn.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False
            print(f"[{addr}] {msg}")
            msg = f"Message received: {msg}"
            barrier.wait()
            conn.send(msg.encode(FORMAT))
    else:
        print(f"[{addr}] {msg}")
        msg = f"Message received: {msg}"
        conn.send(msg.encode(FORMAT))

    conn.close()

def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Client limit is {LIMIT}...")
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    
    while 1:
        conn, addr = server.accept()
        if (threading.activeCount() - 1) >= LIMIT :
            conn.close()
            print(f"[DENYING CONNECTION] Limit of clients reached!")
        else:
            thread = threading.Thread(target=handle_client, args=(conn, addr, barrier))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
if __name__ == "__main__":
    main()