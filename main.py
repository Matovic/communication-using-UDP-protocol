# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import sys
import client
import server


def main():
    if len(sys.argv) != 2:
        print("ERROR 00: Wrong paramaters!")
        sys.exit(-1)

    if sys.argv[1] == 'client':
        client.user_interface()
    elif sys.argv[1] == 'server':
        server.user_interface()
    else:
        print("ERROR 00: Wrong paramaters!")
        sys.exit(-1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
