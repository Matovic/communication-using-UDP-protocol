"""UDP communicator provides client-server communication with file transfer based on UDP.

School assignment n. 2 from course Computer and Communication Networks.
"""

import client
import protocol
import socket
import sys
import os
import select

__author__ = "Erik Matovic"
__version__ = "1.0.0"
__email__ = "xmatovice@stuba.sk"
__status__ = "Production"


def write_msg(server_socket, fragment_size):
    fragment_count = 0
    while True:
        ready = select.select([server_socket], [], [], 3)
        if ready[0]:
            message, client_address = server_socket.recvfrom(protocol.DEFAULT_BUFF)
            reply_crc = protocol.check_crc(message)
            reply = protocol.add_header(reply_crc, fragment_size, b'')
            server_socket.sendto(reply, client_address)
            if reply_crc.value != protocol.MsgType.ACK.value:                       # ARQ Stop & Wait
                continue
            message = protocol.get_data(message)
            print(message.decode('utf-8'), end='')
            fragment_count += 1
        else:
            break
    print('\n', fragment_count)


def write_file(path, server_socket, fragment_size):
    fragment_count = 0
    with open(path, 'wb+') as file:
        while True:
            ready = select.select([server_socket], [], [], 3)
            if ready[0]:
                data, client_address = server_socket.recvfrom(fragment_size)
                reply_crc = protocol.check_crc(data)
                reply = protocol.add_header(reply_crc, fragment_size, b'')
                server_socket.sendto(reply, client_address)

                if reply_crc.value != protocol.MsgType.ACK.value:
                    continue
                data = protocol.get_data(data)
                fragment_count += 1
                file.write(data)
            else:                                                                               # finish
                # print('Finish', file_name)
                break
    print(fragment_count)


def initialization(server_socket):
    while True:
        data, client_address = server_socket.recvfrom(protocol.DEFAULT_BUFF)
        # print('server po ini:', data)
        reply_crc = protocol.check_crc(data)
        reply = protocol.add_header(reply_crc, 0, b'')
        # print(reply, len(reply))
        server_socket.sendto(reply, client_address)
        if reply_crc.value == protocol.MsgType.ACK.value:
            fragment_size = protocol.get_fragmet_size(data) + len(data)
            file_name = protocol.get_file_name(data)
            break
    return data, client_address, fragment_size, file_name


def receive(server_port, dir_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print('Server is ready!')
    data, client_address, fragment_size, file_name = initialization(server_socket)

    if protocol.get_msg_type(data).decode('utf-8') == protocol.MsgType.SET.value:
        write_file(dir_path + file_name, server_socket, fragment_size)
        server_socket.sendto(bytes(protocol.MsgType.ACK.value, 'utf-8'), client_address)
        print('Transfer successful, file at', os.path.abspath(dir_path + file_name))
    else:
        write_msg(server_socket, fragment_size)
    server_socket.close()


def set_server():
    server_port = 0
    dir_path = ''
    while server_port == 0 or dir_path == '':
        try:
            if server_port == 0:
                server_port = int(input('Enter server port to listen: '))

            if server_port < 1024 or server_port > 65535:                   # validate given port
                print('You must enter non - privileged port!')
                server_port = 0
                continue

            dir_path = input('Enter dir path to store files in: ')
            if not os.path.isdir(dir_path):                                 # check if given path is valid
                print('ERROR 01: Path', dir_path, 'does not exist!')
                dir_path = ''
                continue
            if dir_path[:-1] != '/':                                        # check if dir name ends with /
                dir_path += '/'

        except ValueError:                                                  # wrong data type entered
            print('Wrong server port!')
            server_port = 0
            continue

    return server_port, dir_path


def user_interface():
    print('\n{:^50}'.format('server'))
    server_port, dir_path = set_server()
    while True:
        print('0 - end\n'
              '1 - receive\n'
              '9 - change to client')
        user_input = input('Enter what do you want to do: ')
        if user_input == '0':
            print('End')
            sys.exit(0)
        elif user_input == '1':
            receive(server_port, dir_path)
        elif user_input == '9':
            client.user_interface()
        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
