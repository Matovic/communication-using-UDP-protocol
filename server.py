# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import socket
import sys


def receive_message(server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print('Server is ready!')
    while 1:
        message, client_address = server_socket.recvfrom(2048)
        modified_message = message.upper()
        server_socket.sendto(modified_message, client_address)
        if input('End? y/N?') == 'y':
            break
        else:
            print('Server is ready!')


def user_interface():
    try:
        server_port = int(input('Enter server port: '))
        receive_message(server_port)
    except ValueError:
        print('Wrong server port!')
        sys.exit(-1)
