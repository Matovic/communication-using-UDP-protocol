# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import client
import protocol

import socket
import sys
import os
import select


def write_msg(server_socket):
    # while True:
    message, client_address = server_socket.recvfrom(protocol.DEFAULT_BUFF)
    print(message.decode('utf-8'))
    server_socket.sendto(bytes(protocol.MsgReply.ACK.value, 'utf-8'), client_address)
    #   break
    #   if input('End? y/N?') == 'y':
    #       break
    #   else:
    #       print('Server is ready!')


def write_file(path, server_socket, fragment_size):
    with open(path, 'wb+') as file:
        while True:
            ready = select.select([server_socket], [], [], 3)
            if ready[0]:
                data, client_address = server_socket.recvfrom(fragment_size)
                reply = protocol.check_crc(data)
                server_socket.sendto(bytes(reply, 'utf-8'), client_address)

                if reply != protocol.MsgType.ACK.value:
                    continue
                data = protocol.get_data(data)
                file.write(data)
            else:                                                                               # finish
                # print('Finish', file_name)
                break


def receive(server_port, dir_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print('Server is ready!')

    while True:
        data, client_address = server_socket.recvfrom(protocol.DEFAULT_BUFF)
        reply = protocol.check_crc(data)
        server_socket.sendto(bytes(reply, 'utf-8'), client_address)
        if reply == protocol.MsgType.ACK.value:
            fragment_size = protocol.get_fragmet_size(data) + len(data)
            file_name = protocol.get_file_name(data)
            break

    if protocol.get_msg_type(data).decode('utf-8') == protocol.MsgType.SET.value:
        write_file(dir_path + file_name, server_socket, fragment_size)
        server_socket.sendto(bytes(protocol.MsgReply.ACK.value, 'utf-8'), client_address)
        print('Transfer successful, file at', os.path.abspath(dir_path + file_name))
    else:
        write_msg(server_socket)
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

            dir_path = input('Enter file path to store files in: ')
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
