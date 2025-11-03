#!/usr/bin/env python3
import socket
import threading
import datetime
import sys
import random
import os

HOST = "10.199.25.128"
PORT = 5555

clients = {}  # {conn: {"username": str, "color": str}}
log_messages = []
colors = ["\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[91m"]  # green, yellow, blue, magenta, cyan, red
reset = "\033[0m"

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode("utf-8"))
            except:
                remove_client(client)

def remove_client(client):
    if client in clients:
        user = clients[client]["username"]
        log_messages.append(f"[{timestamp()}] {user} left the chat.")
        print(f"[{timestamp()}] {user} disconnected.")
        broadcast(f"\033[90m[{timestamp()}] {user} left the chat.{reset}")
        del clients[client]
        client.close()

def handle_bot(command, client):
    if command == "/help":
        response = "Available commands: /help, /time, /joke, /users"
    elif command == "/time":
        response = f"Server time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elif command == "/joke":
        jokes = [
            "Why do programmers hate nature? Too many bugs.",
            "Debugging: being the detective in a crime you committed.",
            "There are 10 kinds of people: those who understand binary and those who don’t."
        ]
        response = random.choice(jokes)
    elif command == "/users":
        response = "Connected users: " + ", ".join([v['username'] for v in clients.values()])
    else:
        response = "Unknown bot command."
    client.send(f"\033[90m[csi-bot] {response}{reset}\n".encode("utf-8"))

def handle_client(client):
    try:
        client.send("Enter username: ".encode("utf-8"))
        username = client.recv(1024).decode("utf-8").strip()

        client.send("Enter password: ".encode("utf-8"))
        password = client.recv(1024).decode("utf-8").strip()

        if username == "csiadmin" and password != "csiroot":
            client.send("Wrong password for admin.\n".encode("utf-8"))
            client.close()
            return
        elif username != "csiadmin" and password != "csichat":
            client.send("Incorrect password.\n".encode("utf-8"))
            client.close()
            return

        color = "\033[91m" if username == "csiadmin" else random.choice(colors)
        clients[client] = {"username": username, "color": color}

        broadcast(f"\033[90m[{timestamp()}] {username} joined the chat.{reset}")
        log_messages.append(f"[{timestamp()}] {username} joined the chat.")
        print(f"[{timestamp()}] {username} connected.")

        client.send(f"Welcome to CSI Chat, {username}!\nType /help for commands.\n".encode("utf-8"))

        while True:
            msg = client.recv(1024).decode("utf-8")
            if not msg:
                break
            msg = msg.strip()

            if msg.startswith("/"):
                # Handle admin commands
                if username == "csiadmin":
                    if msg.startswith("/kick "):
                        target = msg.split(" ", 1)[1]
                        for c, info in list(clients.items()):
                            if info["username"] == target:
                                c.send("You have been kicked by the admin.\n".encode("utf-8"))
                                remove_client(c)
                                break
                        client.send(f"{target} has been kicked.\n".encode("utf-8"))
                    elif msg == "/stopserver":
                        broadcast("Server is shutting down.\n")
                        for c in list(clients.keys()):
                            c.close()
                        save_log()
                        sys.exit(0)
                    elif msg == "/list":
                        user_list = ", ".join([v['username'] for v in clients.values()])
                        client.send(f"Connected users: {user_list}\n".encode("utf-8"))
                    else:
                        handle_bot(msg, client)
                else:
                    handle_bot(msg, client)
            else:
                formatted = f"[{timestamp()}] {color}{username}{reset} > {msg}"
                log_messages.append(formatted)
                print(formatted)
                broadcast(formatted, client)
    except:
        pass
    finally:
        remove_client(client)

def save_log():
    with open("chat_log.txt", "w") as f:
        for line in log_messages:
            f.write(line + "\n")
    print("Chat log saved to chat_log.txt")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            client, _ = server.accept()
            threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
        save_log()
        for c in list(clients.keys()):
            c.close()
        server.close()
        print("Server cleaned up successfully.")

if __name__ == "__main__":
    start_server()
