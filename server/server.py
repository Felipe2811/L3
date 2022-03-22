import datetime
import functools
import hashlib
import os
import socket
import sys
import threading
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
ADDR = (HOST, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "disc!"
CONNECT_MSG = "OK"
READY_MSG = "READY!"
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 300*2**20

num_clients = 1

def synchronized(wrapped):
    lock = threading.Lock()
    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)
    return _wrap
    
@synchronized
def edit_file(logname, msg):
    with open(f"logs/{logname}", 'a') as outfile:
        # with open(f'logs/Cliente{id_client}-Prueba{num_clients}.txt') as infile:
        outfile.write(msg) 

def handle_client(conn, addr, barrier, hash, filename, logname):
    id_client = str(threading.get_native_id())
    print(f"[CONNECTED] {addr} Client {id_client} connected.")
    msg = conn.recv(BUFFER_SIZE).decode(FORMAT)

    if msg == READY_MSG:
        # SEND Id of the client and OK
        msg = CONNECT_MSG
        conn.send(f"{msg}{SEPARATOR}{id_client}".encode(FORMAT))
        msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
        #print(f"[{addr}] {msg}")
        # WAIT all clients
        file = open(filename, "r")
        data = file.read()
        barrier.wait()

        # SEND filename and filesize
        conn.send(f"{filename}{SEPARATOR}{hash}".encode(FORMAT))

        # RECEIVE confirmation
        msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
        print(f"[{addr}] Client {id_client}: {msg}")

        # SEND data
        start = time.time()
        conn.send(data.encode(FORMAT))

        # RECEIVE Confirmation 
        msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
        total_time = time.time() - start
        #print(f"[{addr}] Client {id_client}: {msg}")
        # SEND time spended
        conn.send(f"{total_time}".encode(FORMAT))

        client_succ = conn.recv(BUFFER_SIZE).decode(FORMAT)
        # with open(f'logs/Cliente{id_client}-Prueba{num_clients}.txt', 'w') as f:
            # f.write(f'[{client_succ}] connected to {addr} with {total_time} s spended.')
        log = f'[{client_succ}] connected to {addr} with {total_time} s spended.\n'
        edit_file(logname, log)

        conn.close()
        file.close()
        print(f"[DISCONNECTED] {addr} Client {id_client} disconnected.")

    else:
        print(f"[{addr}] {msg}")
        msg = f"DENYING CONNECTION"
        conn.send(msg.encode(FORMAT))
        conn.close()

def main():
    # Some parameters
    filename = "prueba.txt"
    num_clients = 1
    if len(sys.argv) > 0:
        filename = sys.argv[1]
        num_clients = int(sys.argv[2])    
    filesize = os.path.getsize(filename)

    num_test = 0
    log = False
    logname = "-"

    print(f"[FILENAME] The filename is: {filename}")
    print(f"[LIMIT] Client limit is {num_clients}...")

    # CALCULATE the hash of the file
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            md5.update(data)
    hash = md5.hexdigest()

    print(f"[HASH] Hash of the file is {hash}")

    # CREATE the barrier for the threads
    barrier = threading.Barrier(num_clients)

    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    
    while 1:
        # if ((threading.activeCount() - 1) == num_clients):
        #     num
        if (threading.activeCount() - 1)  == num_clients and log == True:
            log = False

        if (threading.activeCount() - 1) < num_clients: 
            conn, addr = server.accept()

            if (threading.activeCount() - 1)  == 0 and (log == False):
                print("Creating a new log file")
                date, time = str(datetime.datetime.now()).split(" ")
                hour, minute, second = (time.split(".")[0]).split(":")
                logname = f"{date}-{hour}-{minute}-{second}-log{num_test}.txt"
                log = True
                num_test = num_test + 1

                with open(f"logs/{logname}", 'w') as f:
                    f.write(f'Test: #{num_test}\n')
                    f.write(f'Clients: #{num_clients}\n')
                    f.write(f'Filename: {filename}\n')
                    f.write(f'Filesize: {filesize} bytes\n')
                    f.write(f'Hash: {hash}\n')

            thread = threading.Thread(target=handle_client, args=(conn, addr, barrier, hash, filename, logname))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    main()
