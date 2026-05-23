# Defines fixed parameters
# IP addresses, MAC addresses, routing tables

# IP Addresses
HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"
R1_INTERFACE_1_IP = "10.0.1.1"
R1_INTERFACE_2_IP = "10.0.2.1"

# MAC Addresses
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_B_MAC = "BB:BB:BB:BB:BB:BB"
R1_INTERFACE_1_MAC = "CC:CC:CC:CC:CC:CC"
R1_INTERFACE_2_MAC = "DD:DD:DD:DD:DD:DD"

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
ROUTING_TABLE_HOST_A = {}

ROUTING_TABLE_HOST_B = {}

ROUTING_TABLE_R1 = {}
