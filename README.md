# cits3002-project

CITS3002 Computer Networks Group Project 2026

## Project Summary

This project implements a simplified network simulator that demonstrates how Layer 2, Layer 3, and Layer 4 work together to deliver data from one host to another.

The implementation is divided into four main Python files:
1. `config.py` --
2. `protocol.py` --
3. `devices.py` --
4. `main.py` -- 

## Project Team
|   Student Name   | Student Number | 
|------------------|----------------|
|Kathleen Isabella |    24091081    |
|Kelly Valencia    |    24540356    |

## Project Requirements 
- Python 3.1x
- No external libraries required

## Project Setup
To run the simulator, in the command line interface type: 
```bash
python main.py 100
```
The argument `100` can be changed into any value that represents the application message size (in bytes). In this case, the `100` indicates a 100-byte message. 

## Project Structure
```
cits3002-project/
├── config.py
├── devices.py
├── main.py
├── protocol.py
└── README.md
```

## Further Documentation
For a more detailed explanation on how the project runs, see [24091081-24540356.pdf](24091081-24540356.pdf). 