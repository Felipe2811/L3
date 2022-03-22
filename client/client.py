
import hashlib
import os
import socket
import sys
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (HOST, PORT)
SIZE = 300*2**20
FORMAT = "utf-8"
CONNECT_MSG = "OK"
READY_MSG = "READY!"
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 300*2**20

num_clients = 1

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
        filename = f"Cliente{id}-Prueba{num_clients}.txt"
        # WRITING file
        file = open(filename, "w")

        msg = f"Client {id} received filename and hashcode"
        client.send(msg.encode(FORMAT))

        # RECEIVE data
        data = client.recv(SIZE).decode(FORMAT)
        print(f"[RECV] Data received.")
        file.write(data)
        msg = f"Client {id} received the data"
        file.close()

        # SEND confirmation
        client.send(msg.encode(FORMAT))

        #RECEIVE time spended
        time = client.recv(SIZE).decode(FORMAT)

        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                md5.update(data)

        hash_calc = md5.hexdigest()

        # SEND Integrity confirmation
        if hash_calc == hash_recv:
            msg = f"Client {id} SUCCESFULL"
            client.send(msg.encode(FORMAT))
        else:
            msg = f"Client {id} INTEGRITY ERROR"
            client.send(msg.encode(FORMAT))

        print(f"[HASH] Hash received: {hash_recv}")
        print(f"[HASH] Hash calculated: {hash_calc}")
        print(f"[TRANSFER] {msg}")
        filesize = os.path.getsize(filename)
        print(f"[FILESIZE] Size of the file: {filesize}")
        print(f"[TIME] Time of the transfer: {time}")
        rate = filesize/float(time)
        print(f"[TRANSFER RATE] {rate}")

if __name__ == "__main__":
    num_clients = int(sys.argv[1])
    for i in range(num_clients):
        thread = threading.Thread(target=main)
        thread.start()
    