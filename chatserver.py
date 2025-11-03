#!/usr/bin/env python3
import socket
import threading

HOST = "10.199.25.128"
PORT = 5555

clients = {}
PASSWORD = "csichat"

# Simple colors for each user (ANSI codes)
COLORS = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
]
RESET = "\033[0m"

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                del clients[client]

def handle_client(client_socket, addr):
    print(f"[+] Connection from {addr}")

    # Step 1: Ask for password
    client_socket.send("Enter password: ".encode())
    password = client_socket.recv(1024).decode().strip()
    if password != PASSWORD:
        client_socket.send("Wrong password! Connection closed.\n".encode())
        client_socket.close()
        print(f"[-] {addr} failed authentication")
        return

    # Step 2: Ask for username
    client_socket.send("Password accepted. Enter your username: ".encode())
    username = client_socket.recv(1024).decode().strip()
    color = COLORS[len(clients) % len(COLORS)]
    clients[client_socket] = (username, color)

    broadcast(f"{color}{username}{RESET} joined the chat!", client_socket)
    client_socket.send(f"Welcome to CSI Chat, {username}!\n".encode())

    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg or msg.lower() == "exit":
                break
            broadcast(f"{color}{username}{RESET}: {msg}", client_socket)
        except:
            break

    print(f"[-] {username} disconnected")
    broadcast(f"{color}{username}{RESET} left the chat.", client_socket)
    client_socket.close()
    del clients[client_socket]

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
