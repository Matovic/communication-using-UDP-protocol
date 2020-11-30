# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

# import math
import enum


# HEADER_SIZE = 10
DEFAULT_BUFF = 4096


class MsgType(enum.Enum):
    SET = '0'       # constant for header in initialization for file transfer
    PSH = '1'       # constant for header for pushing for file transfer
    ACK = '2'       # constant for header for positive acknowledgment
    RST = '3'       # constant for header for negative acknowledgment

    SET_MSG = '8'   # constant for header in initialization for msg transfer
    PSH_MSG = '9'   # constant for header for pushing for msg transfer


class MsgReply(enum.Enum):
    SET = 'Initialization successful'   # msg initialization
    ACK = 'Message received!'           # msg for positive acknowledgment
    RST = 'Message corrupted'           # msg for negative acknowledgment


def check_crc(data):
    # if data[7:8].decode('utf-8') != set_crc(data):
    if data[5:6].decode('utf-8') != set_crc(data):
        return MsgType.RST.value
    return MsgType.ACK.value


def set_crc(data):
    checksum = '1'
    return checksum


def get_fragmet_size(data):
    return int(data[1:5].decode('utf-8'))


def get_file_name(data):
    return data[6:].decode('utf-8')


def get_data(data):
    return data[6:]


def get_msg_type(data):
    return data[:1]


def add_header(msg_type, serial_num, fragment_size, data):
    # num_of_fragment = math.ceil(len(data) / fragment_size) \
    #    if len(data) > fragment_size \
    #    else 1
    # checksum = set_crc(data)
    # new_data = bytes(msg_type.value, 'utf-8') + bytes(str(serial_num), 'utf-8') + bytes(str(fragment_size), 'utf-8') \
    #           + bytes(str(num_of_fragment), 'utf-8') + bytes(str(checksum), 'utf-8') + data[:]
    # return new_data
    new_data = bytes(msg_type.value, 'utf-8') + bytes(str(fragment_size), 'utf-8')
    # checksum = set_crc(data)
    new_data += bytes(str(set_crc(data)), 'utf-8') + data
    return new_data


def msg_initialization(fragment_size, file_size, file_name):
    # num_of_fragment = math.ceil(file_size / fragment_size) \
    #    if file_size > fragment_size \
    #    else 1
    # bytes(str(fragment_size), 'utf-8') + \
    # data = bytes(MsgType.SET.value, 'utf-8') + bytes(str(0), 'utf-8') + bytes(str(fragment_size), 'utf-8') + \
    #       bytes(str(num_of_fragment), 'utf-8')
    data = bytes(MsgType.SET.value, 'utf-8') if file_name != MsgType.SET_MSG.value else \
        bytes(MsgType.SET_MSG.value, 'utf-8')
    data += bytes(str(fragment_size), 'utf-8') + bytes(str(set_crc(data)), 'utf-8')
    if file_name == MsgType.SET_MSG.value:
        data += bytes(file_name, 'utf-8')
    else:
        data += file_name
    # checksum = set_crc(data)
    # data += bytes(str(set_crc(data)), 'utf-8') + file_name
    return data
