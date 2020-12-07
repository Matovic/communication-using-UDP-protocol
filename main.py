"""UDP communicator provides client-server communication with file transfer based on UDP.

School assignment n. 2 from course Computer and Communication Networks.
"""

import client
import server
import sys

__author__ = "Erik Matovic"
__version__ = "1.0.1"
__email__ = "xmatovice@stuba.sk"
__status__ = "Production"


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
