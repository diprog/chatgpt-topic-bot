import socket
import select
import struct
import socks

# Set the socks5 proxy address and port number
proxy_address = '138.59.205.239'
proxy_port = 9677

# Set the socks5 proxy username and password
proxy_username = 'GSJYYQ'
proxy_password = 'B6o0FB'

# Set the local proxy server address and port number
local_address = 'localhost'
local_port = 8080

# Create a socks5 proxy object with authentication
proxy = socks.socksocket()
proxy.set_proxy(socks.SOCKS5, proxy_address, proxy_port, True, proxy_username, proxy_password)

# Create a local proxy server socket object
local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the local proxy server socket object to the local_address and local_port
local_server_socket.bind((local_address, local_port))

# Set the local proxy server socket object to listen
local_server_socket.listen(5)

# Create a list of sockets to monitor
sockets = [local_server_socket]

# Create a dictionary to map socket objects to their corresponding destination sockets
mapping = {}

print('Local proxy server started on {}:{}'.format(local_address, local_port))

# Function to handle new connections
def handle_connect(sock):
  # Accept the incoming connection from the local client
  client_socket, client_address = sock.accept()
  print('Accepted connection from {}:{}'.format(client_address[0], client_address[1]))

  # Connect to the destination server via the socks5 proxy
  server_socket = proxy
  server_socket.connect((client_address[0], client_address[1]))

  # Add the sockets to the mapping dictionary
  mapping[client_socket] = server_socket
  mapping[server_socket] = client_socket

  # Add the sockets to the list of sockets to monitor
  sockets.append(client_socket)
  sockets.append(server_socket)

# Function to handle data received on a socket
def handle_data(sock):
  # Receive data from the socket
  data = sock.recv(4096)

  # If no data received, close the sockets and remove them from the list of sockets to monitor
  if not data:
    print('Connection closed')
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    sockets.remove(sock)
    sockets.remove(mapping[sock])
    del mapping[mapping[sock]]
    del mapping[sock]
    return

  # Send the data to the destination socket
  mapping[sock].send(data)

# Main loop to monitor sockets for new connections and data
while True:
  # Use select to monitor the sockets for activity
  readable, _, _ = select.select(sockets, [], [], 1)

  # Handle new connections
  for sock in readable:
    if sock is local_server_socket:
      handle_connect(sock)
    else:
      handle_data(sock)