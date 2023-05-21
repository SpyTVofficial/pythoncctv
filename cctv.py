import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from matplotlib import pyplot as plt
import cv2
import numpy as np


hostname = "0.0.0.0"
webServerPort = 8080
serverPort = 42069

arg = sys.argv[1]

class httpServer(BaseHTTPRequestHandler):
    html_content = "<html><head><title>Home CCTV (0/1)</title></head><body><p>No Cameras detected!</p></body></html>"
    connected = False

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(self.html_content, "utf-8"))

    @classmethod
    def update_html_content(cls, new_content):
        cls.html_content = new_content

    @classmethod
    def update_title(cls, connected):
        if connected:
            cls.html_content = cls.html_content.replace("Home CCTV (0/1)", "Home CCTV (1/1)")
            cls.html_content = cls.html_content.replace("No Cameras detected!", "Camera 1: ")

        else:
            cls.html_content = cls.html_content.replace("Home CCTV (1/1)", "Home CCTV (0/1)")
            cls.html_content = cls.html_content.replace("Camera 1: ", "No Cameras detected!")

def run_http_server():
    webServer = HTTPServer((hostname, webServerPort), httpServer)
    print("WebServer started on Port 8080 ")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((hostname, serverPort))
        s.listen()
        print("CCTV Server started on port 42069")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            httpServer.connected = True  # Update the connection status
            httpServer.update_title(httpServer.connected)  # Update the title when connected
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Update HTML content dynamically when the client connects
            httpServer.connected = False  # Update the connection status
            httpServer.update_title(httpServer.connected)  # Update the title when disconnected

if arg == "server":
    print("Starting CCTV Server!")
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)
    http_thread.start()
    socket_thread.start()
    http_thread.join()
    socket_thread.join()
elif arg == "client":
    print("Starting CCTV Client!")
    connected = False
    while not connected:
        address = input("Enter IP address (press Enter for default): ")
        if address.strip() == "":
            webServerHost = "127.0.0.1"
        else:
            webServerHost = address
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((webServerHost, serverPort))
                connected = True
                print(f"Connected to {webServerHost}:{serverPort}")
                while True:
                    cap = cv2.VideoCapture(1)
                    ret, frame = cap.read()
                    while cap.isOpened():
                        ret, frame = cap.read()
                        s.sendall(frame)
                    cap.release()
                    pass        

        except ConnectionRefusedError:
            print(f"Failed to connect to {webServerHost}:{serverPort}.")
else:
    print("Invalid argument! Use 'server' or 'client' as an argument!")    
