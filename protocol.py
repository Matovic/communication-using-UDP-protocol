# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import math

MSG_TYPE_INITIALIZATION = 0  # constant for header in initialization


def set_crc(data):
    checksum = 1
    return checksum


def add_header(msg_type, serial_num, fragment_size, num_of_fragment, data):
    checksum = set_crc(data)
    new_data = msg_type + serial_num + fragment_size + num_of_fragment + checksum + data[:]
    return new_data


def msg_initialization(fragment_size, data):
    num_of_fragment = math.ceil(data.size() / fragment_size) \
        if data.size() > fragment_size \
        else 1
    add_header(MSG_TYPE_INITIALIZATION, data.size(), fragment_size, num_of_fragment, data)


class Protocol:
    def __init__(self, msg_type, serial_num, size, num_of_fragment, checksum, data):
        self.type = msg_type
        self.serial_num = serial_num
        self.size = size
        self.num_of_fragment = num_of_fragment
        self.checksum = checksum
        self.data = data
