import argparse
import sys
from typing import List

class J1939:
    def __init__(self, can_frame: str):
        self.can_frame = can_frame
        id_and_data = can_frame.split('#', 1)

        if len(id_and_data) != 2:
            raise ValueError(f'ERROR: Invalid CAN Frame: {can_frame}')
        
        self.can_id, self.can_data = id_and_data

        can_id_binary = self.__convert_id_to_binary()
    
        self.priority = int(can_id_binary[0:3], 2)
        self.reserved = int(can_id_binary[3], 2)
        self.data_page = int(can_id_binary[4], 2)
        self.pdu_format = int(can_id_binary[5:13], 2)
        self.pdu_specific = int(can_id_binary[13:21], 2)
        self.source_address = int(can_id_binary[21:29], 2)

        if self.pdu_format < 240:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8) + self.pdu_specific

        else:
            self.pgn = (self.data_page << 16) + (self.pdu_format << 8)

    def __convert_id_to_binary(self) -> str:
        return format(int(self.can_id, 16), '029b')
    
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

def parse_file(file_path:str) -> List[J1939]:
    frames = []
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

    if args.line:
        try:
            frame = J1939(args.line)
            frame.summary()
            
        except ValueError as error:
            print(f'ERROR: {error}')
            sys.exit(1)
    
    elif args.file:
        frames = parse_file(args.file)
        for frame in frames:
            frame.summary()
    
if __name__ == '__main__':
    main()