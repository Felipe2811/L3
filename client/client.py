import hashlib
import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (HOST, PORT)
SIZE = 4096
FORMAT = "utf-8"
CONNECT_MSG = "OK"
READY_MSG = "READY!"
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    msg = READY_MSG
    client.send(msg.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    ans, id = msg.split(SEPARATOR)
    if ans == CONNECT_MSG:
        print(f"[SERVER] {ans}")
        print(f"[CONNECTED] Client {id} connected to server at {HOST}:{PORT}")
        
        # SEND request of file
        msg = f"Client {id} is requesting the filename and the hashcode"
        client.send(msg.encode(FORMAT))
       
        # RECEIVE filename
        msg = client.recv(SIZE).decode(FORMAT)
        filename, hash_recv = msg.split(SEPARATOR) 
        print(f"[RECV] Filename and hash received: \"{filename}\":{hash_recv}") # Print filename and hash received
        
        # WRITING file
        filename = f"{id}-{filename}"
        file = open(filename, "w")

        msg = f"Client {id} received filename and hashcode"
        client.send(msg.encode(FORMAT))

        # RECEIVE data
        data = client.recv(SIZE).decode(FORMAT)
        print(f"[RECV] Data received.")
        file.write(data)
        msg = f"Client {id} received the data"
        client.send(msg.encode(FORMAT))
        file.close()

        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                md5.update(data)

        hash_calc = md5.hexdigest()
        print(f"Hash calculated: {hash_calc}")
        print(f"Hash received: {hash_recv}")

if __name__ == "__main__":
    main()