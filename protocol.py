# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

# import math
import enum


HEADER_SIZE = 6
DEFAULT_BUFF = 4096
DEFAULT_FRAGMENT_LEN = 4
FRAGMENT_MAX = 9999


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


def zero_fill(data):
    count = DEFAULT_FRAGMENT_LEN - len(data) - 1
    new_data = b'0'
    while count > 0:
        new_data += b'0'
        count -= 1
    new_data += data
    return new_data


def check_crc(data):
    # if data[7:8].decode('utf-8') != set_crc(data):
    if data[5:6].decode('utf-8') != set_crc(data):
        return MsgType.RST
    return MsgType.ACK


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


def add_header(msg_type, fragment_size, data):
    fragment_size_bytes = zero_fill(bytes(str(fragment_size), 'utf-8'))
    new_data = bytes(msg_type.value, 'utf-8') + fragment_size_bytes
    new_data += bytes(str(set_crc(data)), 'utf-8') + data
    return new_data


def msg_initialization(fragment_size, file_name):
    # add msg type
    data = bytes(MsgType.SET.value, 'utf-8') if file_name != MsgType.SET_MSG.value else \
        bytes(MsgType.SET_MSG.value, 'utf-8')
    fragment_size_bytes = zero_fill(bytes(str(fragment_size), 'utf-8'))

    # add fragment size and checksum
    data += fragment_size_bytes + bytes(str(set_crc(data)), 'utf-8')

    # add data
    if file_name == MsgType.SET_MSG.value:
        data += bytes(file_name, 'utf-8')
    else:
        data += file_name
    return data
