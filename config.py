## config.py

"""
Defines all the fixed parameters of the simulated network:
IP addresses, MAC addresses, routing tables, and Address Resolution Protocol (ARP)-like tables.
"""

## IP Addresses
NETWORK_1 = "10.0.1.0/24"
NETWORK_2 = "10.0.2.0/24"

HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"

R1_INTERFACE_1_IP = "10.0.1.1"
R1_INTERFACE_2_IP = "10.0.2.1"

## MAC Addresses
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

R1_INTERFACE_1_MAC = "BB:BB:BB:BB:BB:BB"
R1_INTERFACE_2_MAC = "CC:CC:CC:CC:CC:CC"

## Layer 2 Constants
ETHER_TYPE_IPV4 = 0x0800 ## Type field, indicates IPv4 payload

## Layer 3 Constants
DEFAULT_TTL = 100
PROTOCOL_UDP = 17 ## Protocol field, indicates UDP payload

## Layer 4 Constants - Ports (from Protocol Header Definitions examples) & Limits 
SRC_PORT = 5000
DST_PORT = 80

MAX_SEGMENT_SIZE = 500


## Segment Types
DATA_TYPE = 0
ACK_TYPE = 1


## Routing Tables
"""
Format of each entry:
    - "destination_network": ("next_hop_ip", "interface_name")
    - "0.0.0.0" is the default route used when no specific prefix matches/is found
"""

ROUTING_TABLE_HOST_A = {
    NETWORK_1: (HOST_A_IP, "eth0"),        ## Local network   -> send directly to IP address (A)
    "0.0.0.0": (R1_INTERFACE_1_IP, "eth0") ## Everything else -> send to R1 Interface 1
}

ROUTING_TABLE_HOST_B = {
    NETWORK_2: (HOST_B_IP, "eth0"),        ## Local network   -> send directly to IP address (B)
    "0.0.0.0": (R1_INTERFACE_2_IP, "eth0") ## Everything else -> send to R1 Interface 2
}

ROUTING_TABLE_R1 = {
    NETWORK_1: (HOST_A_IP, "eth0"),        ## Network 1 reachable via Interface 1
    NETWORK_2: (HOST_B_IP, "eth1")         ## Network 2 reachable via Interface 2
}

## IP to MAC Mapping (ARP Tables)
"""
Address Resolution Protocol (ARP) Table

Each node must maintain a table that maps the next hop IP address 
(provided by the network layer) to the MAC addresses.

Static/pre-populated tables for simulation
"""

ARP_TABLE_HOST_A = {
    R1_INTERFACE_1_IP: R1_INTERFACE_1_MAC,
}
 
ARP_TABLE_HOST_B = {
    R1_INTERFACE_2_IP: R1_INTERFACE_2_MAC,
}
 
ARP_TABLE_R1 = {
    HOST_A_IP: HOST_A_MAC,   # Host A is reachable via Interface 1
    HOST_B_IP: HOST_B_MAC,   # Host B is reachable via Interface 2
}

# Interface to MAC Mapping for Router R1
"""
R1 sending frame: needs to know which MAC address to use as the
source, depending on which interface it's sending out of
"""

R1_INTERFACE_TO_MAC = {
    "eth0": R1_INTERFACE_1_MAC,
    "eth1": R1_INTERFACE_2_MAC,
}
## R1 receiving frame: reverse map MAC to interface name
R1_MAC_TO_IFACE = {v: k for k, v in R1_INTERFACE_TO_MAC.items()}
