# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import server
import socket
import sys


def send_file(server_ip, server_port, set_fragmentation, file):
    pass


def send_message(server_ip, server_port, set_fragmentation, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message, (server_ip, server_port))
    modified_message, server_address = client_socket.recvfrom(set_fragmentation)
    print(modified_message.decode('utf-8'))
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
              '9 - change to server')
        user_input = input('Enter what do you want to do: ')
        if user_input == '0':
            print('End')
            sys.exit(0)
        elif user_input == '1':
            message = bytes(input('Enter message: '), 'utf-8')
            send_message(server_ip, server_port, fragmentation, message)
        elif user_input == '9':
            server.user_interface()
        else:
            print('\n{:^30}'.format('Wrong input! Try again.\n'))
