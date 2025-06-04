import argparse
import sys
import json
from typing import List

class J1939:
    # Can Frame
    can_frame: str
    can_id: str
    can_data: str

    # Can Frame Data
    priority: int
    reserved: int
    data_page: int
    pdu_format: int
    pdu_specific: int
    source_address: int
    pgn: int

    def __init__(self, can_frame: str):
        self.can_frame = can_frame

        # Separate the ID and Data from the CAN Frame
        id_and_data = can_frame.split('#', 1)

        # Check and see if CAN Frame is in correct format
        if len(id_and_data) != 2:
            raise ValueError(f'ERROR: Invalid CAN Frame: {can_frame}')
        
        self.can_id, self.can_data = id_and_data

        
        # Convert the CAN Id to binary for later processing
        can_id_binary = self.__id_to_binary()
        
        # Extract the fields from binary ID
        self.priority = int(can_id_binary[0:3], 2)
        self.reserved = int(can_id_binary[3], 2)
        self.data_page = int(can_id_binary[4], 2)
        self.pdu_format = int(can_id_binary[5:13], 2)
        self.pdu_specific = int(can_id_binary[13:21], 2)
        self.source_address = int(can_id_binary[21:29], 2)

        self.pgn = self.__determine_pgn()

    # Description: Converts the CAN_ID to binary
    # Parameters: N\A
    # Returns: str
    def __id_to_binary(self) -> str:
        return format(int(self.can_id, 16), '029b')
    
    # Description: Calculate the PGN
    # Parameters: N\A
    # Returns: int
    def __determine_pgn(self) -> int:
        if self.pdu_format < 240:
            return (self.data_page << 16) + (self.pdu_format << 8) + self.pdu_specific
        else:
            return(self.data_page << 16) + (self.pdu_format << 8)

    # Description: Prints a summary of the information gathered
    # Parameters: N\A
    # Returns: N\A
    def summary(self):
        print(f'\nCAN Frame: {self.can_frame}')
        print(f'Source Address: {self.source_address} (0x{self.source_address:X})')
        print(f'PGN: {self.pgn} (0x{self.pgn:X})')
        print("*" * 50)
        
        print(f'Priority: {self.priority}')
        print(f'Reserved: {self.reserved}')
        print(f'Data Page: {self.data_page}')
        print(f'PDU Format: {self.pdu_format} (0x{self.pdu_format:X})')
        print(f'PDU Specific: {self.pdu_specific} (0x{self.pdu_specific:X})\n')

# Description: Parse command line arguments using ArgParse
# Parameters: N\A
# Returns: parse_args object

def parse_arguments():
    parser = argparse.ArgumentParser(
        description = 'Parse J1939 CAN Frames and extract the PGN'
    )

    parser.add_argument(
        '-l', '--line',
        help='Parse a single CAN Frame (Example: 18FEF200#180194018502FFFF)'
    )

    parser.add_argument(
        '-F', '--file',
        help='Parse a J1939 candump formatted J1939 Log File'
    )

    return parser.parse_args()

# Description: Parses a candump-style log file into J1939 Objects
# Parameters: filepath (string)
# Returns: List 
def parse_log_file(file_path: str):
    frames = []

    # Open the file in read mode and parse each line
    try:
        with open(file_path, 'r') as file:
            for line in file:
                frames.append(J1939(line.strip().split(' ')[2]))
    
    except FileNotFoundError:
        print(f'ERROR: {file_path} does not exist')
        sys.exit(2)
    
    except PermissionError:
        print(f'ERROR: Permission denied: {file_path}')
        sys.exit(2)
    
    return frames

def main():
    arguments = parse_arguments()

    if arguments.line:
        try:
            frame = J1939(arguments.line)
            frame.summary()

        except ValueError as error:
            print(f'ERROR: {error}')
            sys.exit(1)
    
    elif arguments.file:
        frames = parse_log_file(arguments.file)
        for frame in frames:
            frame.summary()


if __name__ == '__main__':
    main()