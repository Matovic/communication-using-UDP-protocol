# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import socket
import sys


def send_message(server_ip, server_port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message, (server_ip, server_port))
    modified_message, server_address = client_socket.recvfrom(2048)
    print(modified_message.decode('utf-8'))
    client_socket.close()


def user_interface():
    try:
        server_ip = input('Enter server IP address: ')
        server_port = int(input('Enter server port: '))
        message = bytes(input('Enter message: '), 'utf-8')
        send_message(server_ip, server_port, message)
    except ValueError:
        print('Wrong server port!')
        sys.exit(-1)
