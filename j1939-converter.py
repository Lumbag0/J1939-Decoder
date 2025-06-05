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
    def summary(self, pgn_lookup: dict, spn_lookup: dict):
        pgn_info = pgn_lookup.get(self.pgn)
        
        if pgn_info:
            status = f'{pgn_info.get('parameterGroupLabel')} ({pgn_info.get('acronym')})'
            spns = pgn_info.get('spnList', [])
        
        else:
            status = 'Unknown PGN'
            spns = []
        
        print(f'\nCAN Frame: {self.can_frame}')
        print(f'Source Address: {self.source_address} (0x{self.source_address:X})')
        print(f'PGN: {self.pgn} (0x{self.pgn:X})')
        print(f'Status: {status}')
        print("*" * 50)
        
        print(f'Priority: {self.priority}')
        print(f'Reserved: {self.reserved}')
        print(f'Data Page: {self.data_page}')
        print(f'PDU Format: {self.pdu_format} (0x{self.pdu_format:X})')
        print(f'PDU Specific: {self.pdu_specific} (0x{self.pdu_specific:X})\n')

        if spns:
            self.__print_spns(spns, spn_lookup)
        else:
            print(f'No SPNs found for this PGN ({self.pgn}) in list')
    
    # Description: Print SPNs related to the PGN
    # Parameters: spns (list), spn_lookup (dict)
    # Returns: N\A
    def __print_spns(self, spns: list, spn_lookup: dict):
        print('SPNs:')
        for spn in spns:
            # Find data for current SPN
            spn_info = spn_lookup.get(spn)
            
            if spn_info:
                # Get Spn name (if it does not exist, set it to Unknown)
                name = spn_info.get('spnName', 'Unknown')
                
                # Get Spn description (if it does not exist, set it to nothing)
                desc = spn_info.get('spnDescription', '').split('\r\n')[0]
                
                value = self.decode_spn(self.can_data, spn_info)
                units = spn_info.get('units', '')
                if value is not None:
                    print(f'     {spn}: {name} -- {desc} = {value:}')
                else:
                    print(f'     {spn}: {name} -- [DECODE ERROR]')
            else:
                print(f'     {spn}: No SPN Info')

    # Description: Decodes the value of an SPN from the given bytes using the metadata
    # Parameters: can_data, spn_info dictionary
    # Returns: Float or None
    def decode_spn(self, can_data: str, spn_info: dict) -> float | None:
        try:
            # Convert Hex data to Byte Array
            data_bytes = bytes.fromhex(can_data)

            # Build bitstring
            binary_str = ''.join(f'{byte:08b}' for byte in data_bytes)

            # Get SPN Bit Start and Length
            bit_start = int(spn_info.get('bitPositionStart', 0))
            spn_length = int(spn_info.get('spnLength', 1))

            # Ensure bit start and length does not overflow
            if bit_start + spn_length > len(binary_str):
                print(f'ERROR: SPN {spn_info.get('spnName', 'Unknown')} out of range')
                return None

            # Slice bits representing SPN
            spn_bits = binary_str[bit_start:bit_start + spn_length]

            # Convert string to integer
            value = int(spn_bits, 2)

            # Get Scaling and Offset
            resolution_num = float(spn_info.get('resolutionNumerator', 1))
            resolution_den = float(spn_info.get('resolutionDenominator', 1))
            offset = float(spn_info.get('offset', 0.0))
            scale = resolution_num / resolution_den

            # return scaled value
            return (value * scale) + offset
        
        except Exception as error:
            print(f'ERROR: Failed to decode SPN: {error}')
            return None

class Pgn:
    pgn_file: str
    pgn_data: dict

    def __init__(self, pgn_file: str):
        # Open file and convert to json object for processing
        with open(pgn_file, 'r') as file:
            self.pgn_data = json.load(file)
    
    # Description: Convert PGNs from Sstrings to integers, then filters out empty keys to avoid errors
    # Parameters: N\A
    # Returns: Dict
    def build_pgn_lookup(self) -> dict:
        return {int(key): value for key, value in self.pgn_data.items() if key.strip().isdigit()}

class Spn:
    spn_file: str
    spn_data: dict

    def __init__(self, spn_file: str):
        # Open file and convert to json object for processing
        with open(spn_file) as file:
            self.spn_data = json.load(file)
    
    # Description: Converts SPNs from strings to integers
    # Parameters: N\A
    # Returns: Dict
    def build_spn_lookup(self) -> dict:
        return {int(key): value for key, value in self.spn_data.items() if key.strip().isdigit()}


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
    pgn_data = Pgn(r'pgns_and_spns_json/pgn_list.json')
    spn_data = Spn(r'pgns_and_spns_json/spn_list.json')

    pgn_lookup = pgn_data.build_pgn_lookup()
    spn_lookup = spn_data.build_spn_lookup()

    if arguments.line:
        try:
            frame = J1939(arguments.line)
            frame.summary(pgn_lookup, spn_lookup)

        except ValueError as error:
            print(f'ERROR: {error}')
            sys.exit(1)
    
    elif arguments.file:
        frames = parse_log_file(arguments.file)
        for frame in frames:
            frame.summary(pgn_lookup, spn_lookup)


if __name__ == '__main__':
    main()