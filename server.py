# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import client
import protocol

import socket
import sys
import select


def read_set(data):
    if data[7:8].decode('utf-8') != protocol.set_crc(data):
        return protocol.MsgType.RST.value
    return data[6:7]


def receive_file(server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print('Server is ready!')
    data, client_address = server_socket.recvfrom(2048)

    if data[:1].decode('utf-8') == protocol.MsgType.SET.value:
        num_fragment = read_set(data)
        print('Server is initialized')
    # else:
    #    server_socket.sendto(bytes(protocol.MsgType.RST.value, 'utf-8'), client_address)

    data, client_address = server_socket.recvfrom(2048)
    data = data.decode('utf-8')
    file_name = data.strip()
    with open('file_receive/' + file_name, 'wb+') as file:
        while True:
            ready = select.select([server_socket], [], [], 3)
            if ready[0]:
                data, client_address = server_socket.recvfrom(2048)
                file.write(data)
            else:
                print('Finish', file_name)
                break
    server_socket.sendto(b'Message received!', client_address)
    server_socket.close()


def receive_message(server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print('Server is ready!')
    while 1:
        message, client_address = server_socket.recvfrom(2048)
        print(message.decode('utf-8'))
        server_socket.sendto(b'Message received!', client_address)
        if input('End? y/N?') == 'y':
            break
        else:
            print('Server is ready!')
    server_socket.close()


def set_server():
    server_port = ''
    while server_port == '':
        try:
            server_port = int(input('Enter server port to listen: '))
            if server_port < 1024:                                          # validate given port
                print('You must enter non - privileged port!')
                server_port = ''
                continue
        except ValueError:
            print('Wrong server port!')
            server_port = ''
            continue
    return server_port


def user_interface():
    print('{:^30}'.format('server'))
    server_port = set_server()
    while 1:
        print('0 - end\n'
              '1 - receive\n'
              '2 - file\n'
              '9 - change to client')
        user_input = input('Enter what do you want to do: ')
        if user_input == '0':
            print('End')
            sys.exit(0)
        elif user_input == '1':
            receive_message(server_port)
        elif user_input == '2':
            receive_file(server_port)
        elif user_input == '9':
            client.user_interface()
        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
