import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests

class ProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # Handle HTTPS requests by establishing a tunnel to the server
        host, port = self.path.split(":")
        port = int(port)

        try:
            with socket.create_connection((host, port)) as sock:
                # Send a successful connection response to the client
                self.send_response(200)
                self.end_headers()

                # Set both sockets to non-blocking mode
                self.connection.setblocking(False)
                sock.setblocking(False)

                while True:
                    try:
                        # Use select to check which socket is ready for reading
                        ready_to_read, _, _ = select.select([self.connection, sock], [], [], 0.1)

                        # If client socket has data, forward it to the server
                        if self.connection in ready_to_read:
                            data_from_client = self.connection.recv(4096)
                            if data_from_client:
                                sock.sendall(data_from_client)

                        # If server socket has data, forward it to the client
                        if sock in ready_to_read:
                            data_from_server = sock.recv(4096)
                            if data_from_server:
                                self.connection.sendall(data_from_server)

                        # Break if no data is available from either side
                        if not data_from_client and not data_from_server:
                            break

                    except BlockingIOError:
                        # Ignore non-blocking errors and continue
                        pass

        except Exception as e:
            print(f"Error handling CONNECT: {e}")
            self.send_error(502, "Bad Gateway")

    def do_GET(self):
        self.intercept_request()

    def do_POST(self):
        self.intercept_request()

    def intercept_request(self):
        # Extract request details
        url = f"http://{self.headers['Host']}{self.path}"
        method = self.command
        headers = {key: value for key, value in self.headers.items()}
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Print intercepted request for debugging
        print(f"Intercepted {method} request to {url}")
        print("Headers:", headers)
        print("Body:", body)

        # Forward the request to the target server
        try:
            response = requests.request(method, url, headers=headers, data=body)
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            print(f"Error forwarding request: {e}")
            self.send_error(502, "Bad Gateway")

def run_proxy_server(port=8002):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"Starting proxy server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start the proxy server in a separate thread
    proxy_thread = threading.Thread(target=run_proxy_server)
    proxy_thread.start()
