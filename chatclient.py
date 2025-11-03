#!/usr/bin/env python3
import socket
import threading
import sys
import time

HOST = "10.199.25.128"
PORT = 5555

reset = "\033[0m"

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode("utf-8")
            if not message:
                print("Disconnected from server.")
                break
            print("\r" + message + "\n> ", end="", flush=True)
        except:
            print("\nLost connection to the server.")
            sock.close()
            break

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("⚠️  Server unavailable. Try again later.")
        sys.exit(1)

    print("Connected to CSI Chat Server.\n")

    # Handle login
    def send_input(prompt):
        print(prompt, end="", flush=True)
        return sys.stdin.readline().strip()

    username = send_input("Enter username: ")
    client.send(username.encode("utf-8"))

    password = send_input("Enter password: ")
    client.send(password.encode("utf-8"))

    # Start listening thread
    thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    thread.start()

    print("\nType your messages below. Use /help for commands.")
    print("> ", end="", flush=True)

    # Main chat loop
    while True:
        try:
            message = sys.stdin.readline().strip()
            if not message:
                continue
            if message.lower() in ["/quit", "/exit"]:
                client.send(f"{username} has left the chat.".encode("utf-8"))
                client.close()
                print("Disconnected.")
                break
            client.send(message.encode("utf-8"))
            print("> ", end="", flush=True)
        except (KeyboardInterrupt, EOFError):
            print("\nDisconnected.")
            client.close()
            break

if __name__ == "__main__":
    main()
