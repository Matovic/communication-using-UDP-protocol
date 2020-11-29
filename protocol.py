# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import math
import enum


class MsgType(enum.Enum):
    SET = '0'  # constant for header in initialization
    PSH = '1'  # constant for header for pushing msg
    ACK = '2'
    RST = '3'


def set_crc(data):
    checksum = 1
    return checksum


def add_header(msg_type, serial_num, fragment_size, data):
    num_of_fragment = math.ceil(len(data) / fragment_size) \
        if len(data) > fragment_size \
        else 1
    checksum = set_crc(data)
    new_data = bytes(msg_type.value, 'utf-8') + bytes(str(serial_num), 'utf-8') + bytes(str(fragment_size), 'utf-8') \
               + bytes(str(num_of_fragment), 'utf-8') + bytes(str(checksum), 'utf-8') + data[:]
    return new_data


def msg_initialization(fragment_size, file_size):
    num_of_fragment = math.ceil(file_size / fragment_size) \
        if file_size > fragment_size \
        else 1
    data = bytes(MsgType.SET.value, 'utf-8') + bytes(str(0), 'utf-8') + bytes(str(fragment_size), 'utf-8') + \
           bytes(str(num_of_fragment), 'utf-8')
    checksum = set_crc(data)
    data += bytes(str(checksum), 'utf-8')
    return data
