import sys # For exiting gracefully
import getopt # For taking in user input

class J1939:
    can_frame:str
    can_id:str
    can_data:str
    priority:int
    reserved:int
    data_page:int
    pdu_format:int
    pdu_specific:int
    source_address:int
    pgn:int

    def __init__(self, can_frame):
        self.can_frame = can_frame
        id_and_data = can_frame.split('#', 1)
        
        # Check if it is in the format of a CAN Frame
        if len(id_and_data) != 2:
            raise ValueError(f'ERROR: Invalid CAN Frame: {can_frame}')
        
        self.can_id, self.can_data = id_and_data
        
        # Convert the CAN ID to binary to pull additional data
        can_id_binary = self.__convertIdToBinary()

        self.priority = int(can_id_binary[0:3], 2)
        self.reserved = int(can_id_binary[3], 2)
        self.data_page = int(can_id_binary[4], 2)
        self.pdu_format = int(can_id_binary[5:13], 2)
        self.pdu_specific = int(can_id_binary[13:21], 2)
        self.source_address = int(can_id_binary[21:29], 2)

        # Perform different calculations based on the value of the CAN data page 
        if self.pdu_format < 240:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8) + self.pdu_specific
        else:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8)

    # Description: Converts the CAN ID to integer and then to binary
    # Parameters: N\A
    # Returns: string
    def __convertIdToBinary(self) -> str:
        can_id_integer = int(self.can_id, 16)
        can_id_binary = format(can_id_integer, '029b')

        return can_id_binary
    
    def summary(self):
        print(f'CAN Frame: {self.can_frame}')
        print(f'Source Address: {self.source_address} (0x{self.source_address:X})')
        print(f'PGN: {self.pgn} (0x{self.pgn:X})')
        print(f'---------------------------')
        print(f'Priority: {self.priority}')
        print(f'Reserved: {self.reserved}')
        print(f'Data Page: {self.data_page}')
        print(f'PDU Format: {self.pdu_format} (0x{self.pdu_format:X})')
        print(f'PDU Specific: {self.pdu_specific} (0x{self.pdu_specific:X})')
        print()

# Description: Reads a CAN Log and converts all J1939 into its PGN number
# Parameters: Log File
# Returns: List
def read_file(log_file) -> list:
    frames = []

    # Open the log file in read mode
    with open(f'{log_file}', 'r') as file:

        # Iterate over each line in the file and create an object of J1939 and store it
        for line in file:
            frames.append(J1939(line.strip().split(' ')[2]))

    return frames

def main():
    can_frame = None
    can_file = None
    can_frames = None

    # Iterate over the command line arguments 
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l:F:')

    except getopt.GetoptError as error:
        print(f'ERROR: {error}')
        sys.exit(2)
    
    for opt, arg in opts:
        # Read a single CAN Frame
        if opt == '-l':
            can_frame = J1939(arg)

        # Read a CAN bus log
        if opt == '-F':
            can_file = arg
            can_frames = read_file(can_file)

    if can_frame is not None:
       can_frame.summary()

    if can_frames is not None:
        for frame in can_frames:
            frame.summary()

if __name__ == '__main__':
    main()