import argparse
import sys
from typing import List

class J1939:
    def __init__(self, can_frame: str):
        self.can_frame = can_frame
        id_and_data = can_frame.split('#', 1)
        
        # Check if frame is valid
        if len(id_and_data) != 2:
            raise ValueError(f'ERROR: Invalid CAN Frame: {can_frame}')
        
        self.can_id, self.can_data = id_and_data
        
        # Convert the CAN ID to binary
        can_id_binary = self.__convert_id_to_binary()
    
        # Parse through data and store into variables
        self.priority = int(can_id_binary[0:3], 2)
        self.reserved = int(can_id_binary[3], 2)
        self.data_page = int(can_id_binary[4], 2)
        self.pdu_format = int(can_id_binary[5:13], 2)
        self.pdu_specific = int(can_id_binary[13:21], 2)
        self.source_address = int(can_id_binary[21:29], 2)

        # Calculate the PDU based off PDU Format
        if self.pdu_format < 240:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8) + self.pdu_specific

        else:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8)

    # Description: Converts the CAN ID to binary and returns a string of that binary
    # Parameters: N\A
    # Returns: String
    def __convert_id_to_binary(self) -> str:
        return format(int(self.can_id, 16), '029b')
    
    # Description: Prints a summary of the parsed CAN Frame
    # Parameters: N\A
    # Returns: N\A
    def summary(self):
        print(f'CAN Frame: {self.can_frame}')
        print(f'Source Address: {self.source_address} (0x{self.source_address:X})')
        print(f'PGN: {self.pgn} (0x{self.pgn:X})')
        print('*' * 40)
        print(f'Priority: {self.priority}')
        print(f'Reserved: {self.reserved}')
        print(f'Data Page: {self.data_page}')
        print(f'PDU Format: {self.pdu_format} (0x{self.pdu_format:X})')
        print(f'PDU Specific: {self.pdu_specific} (0x{self.pdu_specific:X})')
        print('-' * 40)
        print()

# Description: Parses the J1939 Log file for CAN IDs and Parses each Frame
# Parameters: File Path to log file
# Returns: List of J1939 Objects
def parse_file(file_path:str) -> List[J1939]:
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

# DescriptionL Using argparse, create a description and add the arguments 
def parse_args():
    parser = argparse.ArgumentParser(
        description='Parse J1939 CAN Frames and extract PGNs'
    )
    
    parser.add_argument(
        '-l', '--line',
        help='Parse a single CAN Frame (e.g., 18FEE000#1BC9A8001BC9A800)'
    )
    
    parser.add_argument(
        '-F', '--file',
        help='Parse a J1939 Log for CAN Frames (in can-utils candump format)'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    # Convert single CAN Frame 
    if args.line:
        try:
            frame = J1939(args.line)
            frame.summary()

        except ValueError as error:
            print(f'ERROR: {error}')
            sys.exit(1)
    
    # Read a log file
    elif args.file:
        frames = parse_file(args.file)
        for frame in frames:
            frame.summary()
    
if __name__ == '__main__':
    main()