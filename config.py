# Defines fixed parameters
# IP addresses, MAC addresses, routing tables

# IP Addresses
NETWORK_1 = "10.0.1.0/24"
NETWORK_2 = "10.0.2.0/24"

HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"

R1_INTERFACE_1_IP = "10.0.1.1"
R1_INTERFACE_2_IP = "10.0.2.1"

# MAC Addresses
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

R1_INTERFACE_1_MAC = "BB:BB:BB:BB:BB:BB"
R1_INTERFACE_2_MAC = "CC:CC:CC:CC:CC:CC"

# Layer 2 Constants
ETHER_TYPE_IPV4 = 0x0800

# Layer 3 Constants
DEFAULT_TTL = 100
PROTOCOL_UDP = 17

# Layer 4 Constants
SRC_PORT = 5000
DST_PORT = 80
MAX_SEGMENT_SIZE = 500

# Segment Types
DATA_TYPE = 0
ACK_TYPE = 1

# Routing Table
# "0.0.0.0" is the default route used when no specific prefix matches
ROUTING_TABLE_HOST_A = {
    NETWORK_1: (HOST_A_IP, "eth0"),        # Local network   -> send directly to IP address (A)
    "0.0.0.0": (R1_INTERFACE_1_IP, "eth0") # Everything else -> send to R1 Interface 1
}

ROUTING_TABLE_HOST_B = {
    NETWORK_2: (HOST_B_IP, "eth0"),        # Local network   -> send directly to IP address (B)
    "0.0.0.0": (R1_INTERFACE_2_IP, "eth0") # Everything else -> send to R1 Interface 2
}

ROUTING_TABLE_R1 = {
    NETWORK_1: (HOST_A_IP, "eth0"), # Network 1 reachable via Interface 1
    NETWORK_2: (HOST_B_IP, "eth1")  # Network 2 reachable via Interface 2
}

# Address Resolution Protocol (ARP) Table 
# Mapping IP address to corresponding MAC Address on local network 
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

# Router R1 Interface to MAC Mapping
R1_INTERFACE_TO_MAC = {
    "eth0": R1_INTERFACE_1_MAC,
    "eth1": R1_INTERFACE_2_MAC,
}
 
R1_MAC_TO_IFACE = {v: k for k, v in R1_INTERFACE_TO_MAC.items()}
