"""UDP communicator provides client-server communication with file transfer based on UDP.

School assignment n. 2 from course Computer and Communication Networks.
"""

import enum
import re

__author__ = "Erik Matovic"
__version__ = "1.0.0"
__email__ = "xmatovice@stuba.sk"
__status__ = "Production"


HEADER_SIZE = 6
DEFAULT_BUFF = 4096
DEFAULT_FRAGMENT_LEN = 4
FRAGMENT_MAX = 1466         # max_fragment = data(1500) - UDP header(8) - IP header(20) - my header(6) = 1466
FRAGMENT_MIN = 1            # min_fragment = data(46) - UDP header(8) - IP header(20) - my header(6) = 12
CRC_KEY = '1001'            # x^3 + 1


class MsgType(enum.Enum):
    """ Enum with constant as signal msg in protocol. """

    SET = '0'       # constant for header in initialization for file transfer
    PSH = '1'       # constant for header for pushing for file transfer
    ACK = '2'       # constant for header for positive acknowledgment
    RST = '3'       # constant for header for negative acknowledgment

    SET_MSG = '8'   # constant for header in initialization for msg transfer


class MsgReply(enum.Enum):
    """ Enum with constant as output for client - server communication. """

    SET = 'Initialization successful'   # msg initialization
    ACK = 'Message received!'           # msg for positive acknowledgment
    RST = 'Message corrupted'           # msg for negative acknowledgment
    KAP = 'Connected'                   # msg for keep alive packet


def zero_fill(data):
    """ Fill fragment size with zeroes if less than default fragment length, which is set to 4.

     data: Data to be filled with zeroes. """

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
    """ Logical XOR method for CRC. Returns string of bits.
    a XOR b

    a: Bit number for XOR.
    b: Bit number for XOR. """

    result = []                                            # initialize result
    for i in range(1, len(b)):                             # go through all bits
        if a[i] == b[i]:                                   # same - XOR is 0
            result.append('0')
            continue
        result.append('1')                                 # not same - XOR is 1
    return ''.join(result)


def sum_checksum(checksum):
    """ Count all bits from given checksum. Return string of this count.

    checksum: Computed checksum to sum all bits. """

    sum_digit = 0
    for char in checksum:
        if char.isdigit():
            sum_digit += int(char)
    return str(sum_digit)


def set_crc(data):
    """ Get checksum based on CRC method. Returns summary of all checksum bits as string.

     data: Data for CRC. """

    crc_key_len = len(CRC_KEY)
    bin_data = (''.join(format(ord(char), 'b') for char in str(data))) + ('0' * (crc_key_len - 1))
    checksum = bin_data[:crc_key_len]
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
    return sum_checksum(checksum)


def check_crc(data):
    """ Check if received data was transferred correctly. Returns positive acknowledgment enum if received data is
    correct, otherwise returns negative acknowledgment enum.

    data: Data contains protocol header with information about original computed checksum. Computing checksum for
    received data and comparing it with original checksum gives a return value. """

    if data[5:6].decode('utf-8') != set_crc(data[6:]):
        return MsgType.RST
    return MsgType.ACK


def get_fragmet_size(data):
    """ Getter method for getting fragment size from protocol header. Returns fragment size as int.

    data: Data contains protocol header with information about fragment size entered by user. """
    return int(data[1:5].decode('utf-8'))


def get_file_name(data, fragment_count):
    """ Getter method for getting file name from protocol header. Returns file name as string.

    data: Data contains received data from transfer initialization with information about file name entered by user. """
    return data[6:-len(fragment_count)].decode('utf-8')


def get_data(data):
    """ Getter method for getting data without protocol header. Returns received data as bytes.

    data: Data contains received data with protocol header. """
    return data[6:]


def get_fragment_count(data, msg_type=None):
    """ Getter method for getting fragment count from data. Returns fragment count as string.
    For text message transfer just returns data from index 7(6-bit header + 1-bit data).
    For file transfer returns last number from data, because data contains also file name it is possible to have data as
    name1.pdf720, where last number 720 is fragment count.

    data: Data contains received data with protocol header. """

    if msg_type == MsgType.SET_MSG.value:
        return data.decode('utf-8')[7:]
    return re.compile(r'\d+').findall(data.decode('utf-8'))[-1:][0]     # regex; getting last number from file name


def get_msg_type(data):
    """ Getter method for getting signal message type.

    data: Data contains received data with protocol header. """
    return data[:1]


def add_header(msg_type, fragment_size, data):
    """ Adding protocol header to data. Returns new data with protocol header as bytes.

    msg_type: Type of message as enum MsgType.
    fragment_size: Maximum size of received data fragment. Entered by a user.
    data: Data contains received data without protocol header. """

    fragment_size_bytes = zero_fill(bytes(str(fragment_size), 'utf-8'))
    new_data = bytes(msg_type.value, 'utf-8') + fragment_size_bytes
    checksum = set_crc(data)
    new_data += bytes(checksum, 'utf-8') + data
    return new_data


def msg_initialization(fragment_size, data):
    """ Adding protocol header to data for initialization. Returns new data with protocol header as bytes.

    fragment_size: Maximum size of received data fragment. Entered by a user.
    data: Data contains received data without protocol header. """

    new_data = bytes(MsgType.SET.value, 'utf-8') if data[:1] != bytes(MsgType.SET_MSG.value, 'utf-8') else \
        bytes(MsgType.SET_MSG.value, 'utf-8')                               # add msg type
    fragment_size_bytes = zero_fill(bytes(str(fragment_size), 'utf-8'))     # fill fragment size with zeros, if less 4
    checksum = set_crc(data)                                                # get checksum
    new_data += fragment_size_bytes + bytes(checksum, 'utf-8')              # add fragment size and checksum
    new_data += data                                                        # add data
    return new_data                                                         # return header + data as new data
