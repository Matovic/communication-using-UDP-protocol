# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import server
import protocol

import socket
import sys
import os
import ntpath
import time


def get_file_name(file_path):
    return ntpath.split(file_path.decode('utf-8'))[1]
    # head, tail = ntpath.split(file_path.decode('utf-8'))
    # print(head, tail)
    # return tail or ntpath.basename(head)


def send_file(server_ip, server_port, fragment_size, file_path):
    file_name = bytes(get_file_name(file_path), 'utf-8')

    file_size = os.path.getsize(file_path)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # set socket
    client_socket.sendto(                                                   # initialization connection
        protocol.msg_initialization(fragment_size, file_size),              # send info about file
        (server_ip, server_port))                                           # server address
    client_socket.sendto(file_name, (server_ip, server_port))
    with open(file_path, 'rb+') as file:
        data = file.read(fragment_size)
        fragment_count = 1
        while data:
            new_data = protocol.add_header(protocol.MsgType.PSH, fragment_count, fragment_size, data)
            if client_socket.sendto(new_data, (server_ip, server_port)):
                data = file.read(fragment_size)
                fragment_count += 1
                time.sleep(0.02)
    modified_message, server_address = client_socket.recvfrom(fragment_size)
    print(modified_message.decode('utf-8'))
    client_socket.close()


def send_message(server_ip, server_port, fragment_size, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message, (server_ip, server_port))
    server_reply, server_address = client_socket.recvfrom(fragment_size)
    print(server_reply.decode('utf-8'))
    client_socket.close()


def set_client():
    server_ip, server_port, fragmentation = '', '', ''
    while server_ip == '' or server_port == '' or fragmentation == '':
        try:
            if server_ip == '':
                server_ip = input('Enter server IP address: ')
                socket.inet_aton(server_ip)                                 # validate given IP address

            if server_port == '':
                server_port = int(input('Enter server port: '))

            if server_port < 1024:                                          # validate given port
                print('You must enter non - privileged port!')
                server_port = ''
                continue

            fragmentation = int(input('Enter max size of fragment: '))

        except ValueError:
            print('Wrong input! Try again')
            server_ip, server_port, fragmentation = '', '', ''
            continue

        except OSError:
            print('Wrong IP address! Try again')
            server_ip = ''
            continue

    return server_ip, server_port, fragmentation


def user_interface():
    print('{:^30}'.format('client'))
    server_ip, server_port, fragmentation = set_client()
    while 1:
        print('0 - end\n'
              '1 - send message\n'
              '2 - send file\n'
              '9 - change to server')
        user_input = input('Enter what do you want to do: ')
        if user_input == '0':
            print('End')
            sys.exit(0)
        elif user_input == '1':
            message = bytes(input('Enter message: '), 'utf-8')
            send_message(server_ip, server_port, fragmentation, message)
        elif user_input == '2':
            file = bytes(input('Enter path to the file: '), 'utf-8')
            if not os.path.isfile(file):                                          # check if given path is valid
                print('ERROR 01: Path', file, 'does not exist!')
                continue
            send_file(server_ip, server_port, fragmentation, file)
        elif user_input == '9':
            server.user_interface()
        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
