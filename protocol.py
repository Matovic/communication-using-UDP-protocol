# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

import enum


HEADER_SIZE = 6
DEFAULT_BUFF = 4096
DEFAULT_FRAGMENT_LEN = 4
FRAGMENT_MAX = 1466         # max_fragment = data(1500) - UDP header(8) - IP header(20) - my header(6) = 1466
FRAGMENT_MIN = 12           # min_fragment = data(46) - UDP header(8) - IP header(20) - my header(6) = 12
CRC_KEY = '1001'            # x^3 + 1


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
    if DEFAULT_FRAGMENT_LEN == len(data):
        return data
    count = DEFAULT_FRAGMENT_LEN - len(data) - 1
    new_data = b'0'
    while count > 0:
        new_data += b'0'
        count -= 1
    new_data += data
    return new_data


def xor(a, b):
    result = []                                            # initialize result
    for i in range(1, len(b)):                             # go through all bits
        if a[i] == b[i]:                                   # same - XOR is 0
            result.append('0')
            continue
        result.append('1')                                 # not same - XOR is 1
    return ''.join(result)


def sum_checksum(checksum):
    sum_digit = 0
    for char in checksum:
        if char.isdigit():
            sum_digit += int(char)
    return str(sum_digit)


def set_crc(data):
    # print('data', str(data), data)
    crc_key_len = len(CRC_KEY)
    bin_data = (''.join(format(ord(char), 'b') for char in str(data))) + ('0' * (crc_key_len - 1))
    # print('bin_data:', bin_data)
    checksum = bin_data[:crc_key_len]
    # print('check pred:', checksum)
    while crc_key_len < len(bin_data):
        if checksum[0] == '1':
            checksum = xor(CRC_KEY, checksum) + bin_data[crc_key_len]
        else:
            checksum = xor('0' * crc_key_len, checksum) + bin_data[crc_key_len]
        crc_key_len += 1
    if checksum[0] == '1':
        checksum = xor(CRC_KEY, checksum)
    else:
        checksum = xor('0' * crc_key_len, checksum)
    # print('check po:', checksum)
    # print('sum', sum_checksum(checksum))
    return sum_checksum(checksum)


def check_crc(data):
    # print('ideme checkuvat', data[6:])
    if data[5:6].decode('utf-8') != set_crc(data[6:]):
        return MsgType.RST
    return MsgType.ACK


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
    # print('+hlavicka', new_data, data)
    checksum = set_crc(data)
    new_data += bytes(checksum, 'utf-8') + data
    # print('+ po hlavicka', new_data)
    return new_data


def msg_initialization(fragment_size, data):
    # add msg type
    new_data = bytes(MsgType.SET.value, 'utf-8') if data != bytes(MsgType.SET_MSG.value, 'utf-8') else \
        bytes(MsgType.SET_MSG.value, 'utf-8')
    fragment_size_bytes = zero_fill(bytes(str(fragment_size), 'utf-8'))

    # print('inicializacia', data)
    # add fragment size

    # add checksum and new_data
    # if data == MsgType.SET_MSG.value:
    #    checksum = set_crc(data)
    #    new_data += fragment_size_bytes + bytes(checksum, 'utf-8')
    #    new_data += bytes(data, 'utf-8')
    # else:
    checksum = set_crc(data)
    new_data += fragment_size_bytes + bytes(checksum, 'utf-8')
    new_data += data
    # print('po inicializacii:', new_data)
    return new_data
