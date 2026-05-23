# cits3002-project

CITS3002 Computer Networks Group Project 2026

## Project Summary

This project implements a simplified network simulator that demonstrates how Layer 2, Layer 3, and Layer 4 work together to deliver data from one host to another.

The simulated network consists of two hosts (Host A and Host B) connected via a router (Router R1), divided across two subnets. A message typed at the command line is segmented and sent from Host A to Host B using a simplified Ethernet-like (Layer 2), IP-like (Layer 3), and UDP-like (Layer 4) protocol stack, with reliable delivery implemented via the rdt2.2 alternating-bit protocol.

The implementation is divided into four main Python files:
1. `config.py` -- Defines all fixed network parameters: IP addresses, MAC addresses, routing tables, and ARP tables for each device.
2. `protocol.py` -- Defines the data structures for each layer: `Frame` (Layer 2), `Packet` (Layer 3), and `Segment` (Layer 4), including checksum computation and verification.
3. `devices.py` -- Implements the `Host` and `Router` classes, containing the full logic for sending, receiving, routing, and forwarding data across all three layers.
4. `main.py` -- Entry point. Parses the command-line argument, constructs the network devices, and initiates the simulation by sending data from Host A to Host B.

## Project Team
|   Student Name   | Student Number | 
|------------------|----------------|
|Kathleen Isabella |    24091081    |
|Kelly Valencia    |    24540356    |

## Project Requirements 
- Python 3.10 or later
- No external libraries required (standard library only)

## Running the Simulator
To run the simulator, in the command line interface type: 
```bash
python main.py <message_size> 
```
Where <message_size> is a positive integer representing the application message size in bytes.  For example:
- `python main.py 10` --> Sends a 10-byte message
- `python main.py 100` --> Sends a 100-byte message
- `python main.py 1200` --> Sends a 1200-byte message (split into 3 segments)

Messages larger than 500 bytes are automatically split into multiple 500-byte segments, each transmitted and acknowledged individually.

## Project Structure
```
cits3002-project/
├── config.py   ## Network parameters (IPs, MACs, routing tables, ARP tables)
├── devices.py  ## Host and Router class implementations
├── main.py     ## Entry point and simulation 
├── protocol.py ## Layer 2/3/4 header class definitions
└── README.md
```

## Further Documentation
For a more detailed explanation on how the project runs, see [24091081-24540356.pdf](24091081-24540356.pdf). 