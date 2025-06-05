# J1939-Decoder
J1939-Decoder is a Python script that takes a CAN Frame and parses through to obtain the PGN, SPNs, and tries to obtain the SPN data. 
J1939-Decoder uses the pgn and spn list JSON files found in LittleBlondeDevil's [TruckDevil](https://github.com/LittleBlondeDevil/TruckDevil) repository.

## Features
- Uses standard python libraries
- Parse a single CAN Frame
- Parse a log file from candump
- Output to a file

## Installation

### 1. Clone the Repository
```
git clone https://github.com/Lumbag0/J1939-Decoder.git
```

## Example Usage
### Running against a file and outputting results to a file
```
python3 J1939-decoder/j1939-converter -F j1939.log -o output.txt
```
### Running against a line
```
python3 J1939-decoder/j1939-converter -l 18FEF200#180194018502FFFF
```