# J1939-Decoder
J1939-Decoder is a Python script that takes a CAN Frame and parses through to obtain the PGN along with other data

## Features
- Parse a single CAN Frame
- Parse a log file from candump

## Installation

### 1. Clone the Repository
```
git clone https://github.com/Lumbag0/J1939-Decoder.git
```

### 2. Install necessary packages

```
pip3 install -r J1939-Decoder/requirements.txt
```

## Example Usage
```
python3 J1939-decoder/j1939-converter -F j1939.log
```