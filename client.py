"""UDP communicator provides client-server communication with file transfer based on UDP.

School assignment n. 2 from course Computer and Communication Networks.
"""

import server
import protocol
import select
import socket
import sys
import os
import ntpath
import math
import time

__author__ = "Erik Matovic"
__version__ = "1.0.0"
__email__ = "xmatovice@stuba.sk"
__status__ = "Production"


def get_file_name(file_path):
    """ Get file name from file path. Returns name of a file.

     file_path: Given path from user to file to be transferred. """
    return ntpath.split(file_path.decode('utf-8'))[1]


def initialization(client_socket, server_ip, server_port, fragment_size, data):
    """ Text or file transfer initialization.

     client_socket: Client socket contains source address and sendto method.
     server_ip: One part of a target address in socket
     server_port: Second part of a target address in socket
     fragment_size: Maximum size of one fragment given by user
     data: Data of text transfer contains one byte telling protocol to add msg type as text transfer.
           Data of file transfer contains name of a file to be created on a server.
           Rest is number of fragments both for text transfer and file transfer. """
    try:
        while True:
            client_socket.sendto(  # initialization connection
                protocol.msg_initialization(fragment_size, data),  # send info about file
                (server_ip, server_port))  # server address
            ready = select.select([client_socket], [], [], 5)
            if ready[0]:
                new_data, server_address = client_socket.recvfrom(fragment_size)
            else:
                print('Connection not established')
                return 0

            if new_data[:1].decode('utf-8') == protocol.MsgType.ACK.value:
                break
        print(protocol.MsgReply.SET.value)

    except ConnectionResetError:
        print('Connection lost. Turn server on.')
    return 1


def send_file(server_ip, client_socket, server_port, fragment_size, file_path):
    """ File transfer.

     client_socket: Client socket contains source address and sendto method.
     server_ip: One part of a target address in socket
     server_port: Second part of a target address in socket
     fragment_size: Maximum size of one fragment given by user
     file_path: Containt file to be open for reading and fo data bytes tranfers. """

    user_input_mistake = input('Make a mistake in transfer? y/n ')
    if user_input_mistake.lower() != 'y' and user_input_mistake.lower() != 'n':
        print('Wrong input!')
        send_file(server_ip, client_socket, server_port, fragment_size, file_path)

    file_name = bytes(get_file_name(file_path), 'utf-8')
    file_size = os.path.getsize(file_path)
    num_of_fragment = math.ceil(file_size / (fragment_size - protocol.HEADER_SIZE))

    try:
        if initialization(client_socket, server_ip, server_port, fragment_size,
                          file_name + bytes(str(num_of_fragment), 'utf-8')) == 0:
            return
        start_time = time.time()
        with open(file_path, 'rb+') as file:
            data = file.read(fragment_size - protocol.HEADER_SIZE)
            fragment_count = 0
            while data:
                new_data = protocol.add_header(protocol.MsgType.PSH, fragment_size, data)
                if user_input_mistake == 'y':
                    header = new_data[:6]
                    new_data = header + new_data[10:]
                    user_input_mistake = 'n'
                if client_socket.sendto(new_data, (server_ip, server_port)):
                    reply, server_address = client_socket.recvfrom(fragment_size)
                    if reply[:1].decode('utf-8') != protocol.MsgType.ACK.value:  # ARQ Stop & Wait
                        print('negative acknowledgment msg')
                        continue

                    data = file.read(fragment_size - protocol.HEADER_SIZE)
                    fragment_count += 1

        ready = select.select([client_socket], [], [], 5)
        if ready[0]:
            if client_socket.recvfrom(fragment_size):
                end_time = time.time()
                print(protocol.MsgReply.ACK.value)
                print('Time:', end_time - start_time)
                print('File at', os.path.abspath(file_path.decode('utf-8')))
                print('Send fragments are', fragment_count, 'and counted fragments are', num_of_fragment, '\n')
        else:
            print('Connection not established')
            return

    except ConnectionResetError:
        print('Connection lost. Turn server on.')


def send_message(server_ip, client_socket, server_port, fragment_size, message):
    """ Text message transfer.

     client_socket: Client socket contains source address and sendto method.
     server_ip: One part of a target address in socket
     server_port: Second part of a target address in socket
     fragment_size: Maximum size of one fragment given by user
     Message: Data to be transferred. """

    fragment_count = 0
    num_of_fragment = math.ceil(len(message.decode('utf-8')) / fragment_size)

    try:
        if initialization(client_socket, server_ip, server_port, fragment_size + protocol.HEADER_SIZE,
                          bytes(protocol.MsgType.SET_MSG.value, 'utf-8') + bytes(str(num_of_fragment), 'utf-8')) == 0:
            return
        lenght = math.ceil(len(message) / fragment_size)
        # server_reply = ''
        index1, index2 = 0, fragment_size

        while lenght > 0:
            data = protocol.add_header(protocol.MsgType.PSH, fragment_size, message[index1:index2])
            client_socket.sendto(data, (server_ip, server_port))
            ready = select.select([client_socket], [], [], 5)
            if ready[0]:
                if client_socket.recvfrom(fragment_size + protocol.HEADER_SIZE):
                    index1 += fragment_size
                    index2 += fragment_size
                    lenght -= 1
                    fragment_count += 1
            else:
                print('Connection not established')
                return

    except ConnectionResetError:
        print('Connection lost. Turn server on.')
    print('Send fragments are', fragment_count, 'and counted fragments are', num_of_fragment, '\n')


def set_client():
    """ Initial client settings. Returns server_ip, client_port, server_port, fragmentation entered by user. """

    server_ip, client_port, server_port, fragmentation = '', '', '', ''
    while server_ip == '' or server_port == '' or fragmentation == '':  # read values to set client
        try:
            if server_ip == '':
                server_ip = input('Enter server IP address: ')
                socket.inet_aton(server_ip)  # validate given IP address

            if client_port == '':
                client_port = int(input('Enter client/source port: '))

            if client_port < 1024 or client_port > 65535:  # validate given port
                print('You must enter non - privileged port!')
                client_port = ''
                continue

            if server_port == '':
                server_port = int(input('Enter server port: '))

            if server_port < 1024 or server_port > 65535:  # validate given port
                print('You must enter non - privileged port!')
                server_port = ''
                continue

            fragmentation = int(input('Enter max size of fragment: '))

            if fragmentation < protocol.FRAGMENT_MIN:  # validate given  value of fragment
                fragmentation = protocol.FRAGMENT_MIN

            if fragmentation > protocol.FRAGMENT_MAX:  # validate max fragment
                fragmentation = protocol.FRAGMENT_MAX

        except ValueError:  # wrong data type entered
            print('Wrong input! Try again')
            server_ip, server_port, fragmentation = '', '', ''
            continue

        except OSError:  # wrong IP address entered
            print('Wrong IP address! Try again')
            server_ip = ''
            continue

    return server_ip, client_port, server_port, fragmentation


def user_interface():
    """ Client user interface. """

    print('\n{:^50}'.format('client'))
    server_ip, client_port, server_port, fragmentation = set_client()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # set socket with IPv4 and UPD
    client_socket.bind(('', client_port))  # set source port

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

        if user_input == '1':
            message = bytes(input('Enter message: '), 'utf-8')
            send_message(server_ip, client_socket, server_port, fragmentation, message)

        elif user_input == '2':
            file = bytes(input('Enter path to the file: '), 'utf-8')
            if not os.path.isfile(file):  # check if given path is valid
                print('ERROR 01: Path', file.decode('utf-8'), 'does not exist!')
                continue
            send_file(server_ip, client_socket, server_port, fragmentation + protocol.HEADER_SIZE, file)

        elif user_input == '9':
            client_socket.close()
            server.user_interface()

        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
