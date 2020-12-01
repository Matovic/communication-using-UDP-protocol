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


def initialization(client_socket, server_ip, server_port, fragment_size, data):
    while True:
        client_socket.sendto(                                               # initialization connection
            protocol.msg_initialization(fragment_size, data),               # send info about file
            (server_ip, server_port))                                       # server address
        print(fragment_size)
        new_data, server_address = client_socket.recvfrom(fragment_size)
        if new_data[:1].decode('utf-8') == protocol.MsgType.ACK.value:
            break
    print(protocol.MsgReply.SET.value)


def send_file(server_ip, client_socket, server_port, fragment_size, file_path):
    file_name = bytes(get_file_name(file_path), 'utf-8')

    file_size = os.path.getsize(file_path)
    try:
        initialization(client_socket, server_ip, server_port, fragment_size, file_name)
        with open(file_path, 'rb+') as file:
            data = file.read(fragment_size)
            fragment_count = 1
            while data:
                new_data = protocol.add_header(protocol.MsgType.PSH, fragment_size, data)
                if client_socket.sendto(new_data, (server_ip, server_port)):
                    data, server_address = client_socket.recvfrom(fragment_size)
                    if data[:1].decode('utf-8') != protocol.MsgType.ACK.value:
                        print('negative acknowledgment msg')
                        continue
                    print('positive acknowledgment msg')
                    data = file.read(fragment_size)
                    fragment_count += 1
                    time.sleep(0.02)
        modified_message, server_address = client_socket.recvfrom(fragment_size)
        print(modified_message.decode('utf-8'))
    except ConnectionResetError:
        print('ERROR SERVER: Server closed connection - server is turned off or you entered wrong port or IP address')


def send_message(server_ip, client_socket, server_port, fragment_size, message):
    try:
        initialization(client_socket, server_ip, server_port, fragment_size, protocol.MsgType.SET_MSG.value)
        client_socket.sendto(message, (server_ip, server_port))
        server_reply, server_address = client_socket.recvfrom(fragment_size)
        print(server_reply.decode('utf-8'))
    except ConnectionResetError:
        print('ERROR SERVER: Server closed connection - server is turned off or you entered wrong port or IP address')


def set_client():
    server_ip, client_port, server_port, fragmentation = '', '', '', ''
    while server_ip == '' or server_port == '' or fragmentation == '':      # read values to set client
        try:
            if server_ip == '':
                server_ip = input('Enter server IP address: ')
                socket.inet_aton(server_ip)                                 # validate given IP address

            if client_port == '':
                client_port = int(input('Enter client/source port: '))

            if client_port < 1024 or client_port > 65535:                   # validate given port
                print('You must enter non - privileged port!')
                client_port = ''
                continue

            if server_port == '':
                server_port = int(input('Enter server port: '))

            if server_port < 1024 or server_port > 65535:                   # validate given port
                print('You must enter non - privileged port!')
                server_port = ''
                continue

            fragmentation = int(input('Enter max size of fragment: '))
            if fragmentation < 1:                                           # validate given max value of fragment
                print('You cannot have fragments less than 1!')
                fragmentation = ''
                # continue

            if fragmentation > protocol.FRAGMENT_MAX:                       # validate max fragment
                fragmentation = protocol.FRAGMENT_MAX

        except ValueError:                                                  # wrong data type entered
            print('Wrong input! Try again')
            server_ip, server_port, fragmentation = '', '', ''
            continue

        except OSError:                                                     # wrong IP address entered
            print('Wrong IP address! Try again')
            server_ip = ''
            continue

    return server_ip, client_port, server_port, fragmentation


def user_interface():
    print('\n{:^50}'.format('client'))
    server_ip, client_port, server_port, fragmentation = set_client()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                    # set socket with IPv4 and UPD
    client_socket.bind(('', client_port))                                               # set source port

    while True:
        print('0 - end\n'
              '1 - send message\n'
              '2 - send file\n'
              '9 - change to server')
        user_input = input('Enter what do you want to do: ')
        if user_input == '0':
            print('End')
            client_socket.close()
            sys.exit(0)
        elif user_input == '1':
            message = bytes(input('Enter message: '), 'utf-8')
            send_message(server_ip, client_socket, server_port, fragmentation + protocol.HEADER_SIZE, message)
        elif user_input == '2':
            file = bytes(input('Enter path to the file: '), 'utf-8')
            if not os.path.isfile(file):                                          # check if given path is valid
                print('ERROR 01: Path', file, 'does not exist!')
                continue
            send_file(server_ip, client_socket, server_port, fragmentation + protocol.HEADER_SIZE, file)
        elif user_input == '9':
            client_socket.close()
            server.user_interface()
        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
