import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "disc!"
CONNECT_MSG = "OK"
READY_MSG = "READY!"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = False
    msg = READY_MSG
    client.send(msg.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    if msg == CONNECT_MSG:
        print(f"[SERVER] {msg}")
        print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")
        connected = True

    while connected:
        msg = input("> ")
        client.send(msg.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
        else:
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

if __name__ == "__main__":
    main()