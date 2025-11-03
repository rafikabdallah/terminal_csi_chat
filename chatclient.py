#!/usr/bin/env python3
import socket
import threading
import sys

SERVER_IP = "10.199.25.128"
PORT = 5555

def receive(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            print(data)
        except:
            print("Disconnected from server.")
            sock.close()
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_IP, PORT))
except:
    print("Unable to connect to server.")
    sys.exit()

thread = threading.Thread(target=receive, args=(client,))
thread.daemon = True
thread.start()

while True:
    msg = input()
    if msg.lower() == "exit":
        client.close()
        break
    client.send(msg.encode())

