import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, Response
import socket
import cv2
import numpy as np
from matplotlib import pyplot as plt


hostname = "0.0.0.0"
webServerPort = 8080
serverPort = 42069

arg = sys.argv[1]

class httpServer(BaseHTTPRequestHandler):
    html_content = "<html><head><title>Home CCTV (0/1)</title></head><body><p>No Cameras detected!</p><a href='dashboard.html'>Dashboard</a></body></html>"
    connected = False

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(httpServer.html_content, "utf-8"))

    @classmethod
    def update_html_content(cls, new_content):
        cls.html_content = new_content

    @classmethod
    def update_title(cls, connected):
        if connected:
            cls.html_content = cls.html_content.replace("Home CCTV (0/1)", "Home CCTV (1/1)")
            cls.html_content = cls.html_content.replace("No Cameras detected!", "Camera 1: <img style=\"display: block; \" src=\"http://127.0.0.1:5000/video_feed\">")
        else:
            cls.html_content = cls.html_content.replace("Home CCTV (1/1)", "Home CCTV (0/1)")
            cls.html_content = cls.html_content.replace("Camera 1: <img style=\"display: block; \" src=\"http://127.0.0.1:5000/video_feed\">", "No Cameras detected!")

    @classmethod
    def set_latest_frame(cls, frame):
        cls.latest_frame = frame

    @classmethod
    def get_latest_frame(cls):
        return cls.latest_frame

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
                frame = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                httpServer.set_latest_frame(frame)
            httpServer.connected = False  # Update the connection status
            httpServer.update_title(httpServer.connected)  # Update the title when disconnected
            print("Client disconnected.")
                # close the already opened camera
            camera.release()
            # close the already opened file
            output.release()
            # close the window and de-allocate any associated memory usage
            cv2.destroyAllWindows()  

def gen_frames():
    #Capture video from webcam
    #vid_capture = cv2.VideoCapture(0)
    vid_cod = cv2.VideoWriter_fourcc(*'mp4v')
    global output
    output = cv2.VideoWriter("videos/cam_video.mp4", vid_cod, 20.0, (640,480))
    while True:
        success, frame = camera.read()  # read the camera frame
         # Capture each frame of webcam videoss
        # ret,frame = camera.read()
        cv2.imshow("My cam video", frame)
        output.write(frame)
        # Close and break the loop after pressing "x" key
        if cv2.waitKey(1) &0XFF == ord('x'):
         break
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    
if arg == "server":
    print("Starting CCTV Server!")
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)
    http_thread.start()
    socket_thread.start()
    http_thread.join()
    socket_thread.join()

elif arg == "client":

    camera = cv2.VideoCapture(0)
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        return render_template('dashboard.html')

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
                    app.run(debug=False, host='0.0.0.0', port=5000)
                    pass        

        except ConnectionRefusedError:
            print(f"Failed to connect to {webServerHost}:{serverPort}.")
else:
    print("Invalid argument! Use 'server' or 'client' as an argument!")
