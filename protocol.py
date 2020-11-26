# Erik Matovic
# PKS
# Zadanie 2: UDP communicator

class Protocol:
    def __init__(self, msg_type, serial_num, size, num_of_fragment, checksum, data):
        self.type = msg_type
        self.serial_num = serial_num
        self.size = size
        self.num_of_fragment = num_of_fragment
        self.checksum = checksum
        self.data = data
