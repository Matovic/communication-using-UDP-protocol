# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import client
import server

import sys


def main():
    if len(sys.argv) != 2:
        print("ERROR 00: Wrong parameters!")
        sys.exit(-1)

    if sys.argv[1] == 'client':
        client.user_interface()
    elif sys.argv[1] == 'server':
        server.user_interface()
    else:
        print("ERROR 00: Wrong parameters!")
        sys.exit(-1)


if __name__ == '__main__':
    main()
