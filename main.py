
import socket
import threading
import os
import time
from datetime import datetime
print("Please click here : http://127.0.0.1:8000/")

class MyWebServer(object):

    def __init__(self, server_address):
        # Create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind(server_address)

        self.server_socket.listen(5)

    def run(self):

        while True:

            client_connection, client_address = self.server_socket.accept()

            client_connection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            client_connection.ioctl(socket.SIO_KEEPALIVE_VALS,(1, 60*1000, 30*1000))
            #After 1 minute, if the other party has not reacted, start to probe whether the connection exists, probe
            #once every 60 seconds, the default probe is ten times, and if it fails, it will be disconnected
            #This implements the keep alive function of this program

            # Send HTTP response
            thread = threading.Thread(target=self.handle_request, args=(client_connection,))
            thread.start()

            #This implements the Multi-threaded function of this program

            #We cannot do client_connection.close() here for child processes to use client_connection


    # Handle the HTTP request.
    def handle_request(self, client_connection):
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S'
        # Parse HTTP headers
        # Get the client request
        global ifmodified
        global first1
        global first
        request = client_connection.recv(1024).decode()
        headers = request.split('\n')
        fields = headers[0].split()
        request_type = fields[0]
        filename = fields[1]
        # Parse the request type
        print('request:\n')
        print(request)
        # Handle the HTTP request.
        with open("htdocs/textlog.txt", encoding="utf-8", mode="a") as file:
            line = datetime.utcnow().strftime(GMT_FORMAT) + "   "+headers[0]+headers[1]+headers[2]+"\n\n"
            file.write(line)

        # Handle the GET request.

        if request_type == 'GET':
            # Get the content of the file

            if filename == '/':
                filename = '/index.html'
            try:
                mtime = time.localtime(os.stat('htdocs' + filename).st_mtime)
                modify_time = time.strftime(GMT_FORMAT, mtime)
                now_time = datetime.utcnow().strftime(GMT_FORMAT)
                dt1 = datetime.strptime(modify_time, GMT_FORMAT)
                if ".jpg" in request:
                    if dt1 < ifmodified and first1 is not True:
                        response = 'HTTP/1.1 304 Not Modified\nLast_Modified: {0}\n'.format(modify_time)
                        client_connection.sendall(response.encode())
                        # return 304 because the file not modified


                    else:
                        ifmodified = datetime.now()
                        response = 'HTTP/1.1 200 OK\nLast_Modified: {0}\n'.format(modify_time)
                        #command finish successfully
                        first1 = False
                        client_connection.sendall(response.encode())
                    response = 'If-Modified-Since: {0}\n\n'.format(now_time)
                    client_connection.sendall(response.encode())

                    fin = open('htdocs/image.jpg', "rb")
                    content = fin.read()
                    fin.close()
                    client_connection.sendall(content)
                    #In order for the image to be displayed properly in the browser, here we send the header and the image separately
                    #This implements the GET command for image file function of this program

                else:
                    if dt1 < ifmodified and first is not True:
                        response = 'HTTP/1.1 304 Not Modified\nLast_Modified: {0}\n'.format(modify_time)
                        client_connection.sendall(response.encode())
                        # return 304 because the file not modified


                    else:
                        ifmodified = datetime.now()
                        response = 'HTTP/1.1 200 OK\nLast_Modified: {0}\n'.format(modify_time)
                        #command finish successfully
                        first1 = True
                        client_connection.sendall(response.encode())
                    fin = open('htdocs' + filename)
                    content = fin.read()
                    fin.close()
                    response = 'If-Modified-Since: '+now_time+'\n\n'+content
                    client_connection.sendall(response.encode())
                    # This implements the GET command txt file function of this program

            except FileNotFoundError:
                response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
                # return 404 because the file cant find
                client_connection.sendall(response.encode())
        # Handle the HEAD request.

        elif request_type == 'HEAD':

            if filename == '/':
                filename = '/index.html'
            try:
                mtime = time.localtime(os.stat('htdocs' + filename).st_mtime)
                modify_time = time.strftime(GMT_FORMAT, mtime)
                now_time = datetime.utcnow().strftime(GMT_FORMAT)
                dt1 = datetime.strptime(modify_time, GMT_FORMAT)
                if dt1 < ifmodified and first is not True:
                    response = 'HTTP/1.1 304 Not Modified\nLast_Modified: {0}\n'.format(modify_time)
                    # return 304 because the file not modified
                    client_connection.sendall(response.encode())

                else:
                    ifmodified = datetime.now()
                    response = 'HTTP/1.1 200 OK\nLast_Modified: {0}\n'.format(modify_time)
                    # command finish successfully

                    first = False
                    client_connection.sendall(response.encode())

                fin = open('htdocs' + filename)
                content = fin.read()
                fin.close()

                # command finish successfully

                response = 'If-Modified-Since: {0}\n\n'.format(now_time)
                client_connection.sendall(response.encode())

            except FileNotFoundError:
                response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
                #return 404 because the file cant find
                client_connection.sendall(response.encode())
        # Handle the other request.
        else:

            response = 'HTTP/1.1 400 Bad Request\n\nRequest Not Supported'
            #return status 400 because we can not handle this request
            client_connection.sendall(response.encode())
        # This implements the HEAD command function of this program

        client_connection.close()
        # Close socket


# Define socket host and port

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)
ifmodified = datetime.now()
first = True
first1= True
def main():

    print('Listening on port %s ...' % SERVER_PORT)
    MyWebServer(SERVER_ADDR).run()


if __name__ == "__main__":
    main()
