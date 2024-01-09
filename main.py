import pathlib
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import socket
import mimetypes
from threading import Thread
import datetime

BASE_DIR = pathlib.Path()
BUFFER_SIZE = 1024
HTTP_PORT = 8080
HTTP_HOST = '0.0.0.0'
SOCKET_PORT = 5000
SOCKET_HOST = '127.0.0.1'


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        if path == '/':
            self.index()
        elif path == '/message':
            self.message()
        else:
            if path:
                file = BASE_DIR.joinpath(path[1:])
                if file.exists():
                    self.send_static(file)
            self.page_not_found()

    def index(self):
        self.send_html_file('index.html')

    def message(self):
        self.send_html_file('message.html')

    def page_not_found(self):
        self.send_html_file('error.html', status=404)

    def send_html_file(self, filename, status=200):
        with open(filename, 'rb') as f:
            response_content = f.read()
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(response_content)))
        self.end_headers()
        self.wfile.write(response_content)

    def send_static(self, file):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(file, 'rb') as f:
            self.wfile.write(f.read())


def save_data_to_json(data):
    data_parse = urllib.parse.unquote(data.decode())
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        logging.info('1')
        with open('storage/data.json', 'r+', encoding='utf-8') as file:
            logging.info('2')
            file_data = json.load(file)
            logging.info('3')
            logging.info(f'data: {file_data}')

            file_data[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = parse_dict
            file.seek(0)
            json.dump(file_data, file, ensure_ascii=False, indent=4)

    except ValueError as error:
        logging.error(error)
    except OSError as error:
        logging.error(error)


def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info("Starting socket server")
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f"Socket received: {msg.decode()} from {address}")
            save_data_to_json(msg)
    except KeyboardInterrupt:
        logging.error("Socket server error")
    finally:
        server_socket.close()


def run_http_server(host, port):
    server_address = (host, port)
    http = HTTPServer(server_address, HttpHandler)
    logging.info("Starting http server")
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.error("Http server error")
        http.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    socket_server = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    socket_server.start()
