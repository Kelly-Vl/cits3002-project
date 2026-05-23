# =============================================================================
# protocol.py
# =============================================================================

# Defines the data structures (header definitions and classes) for each layer:
#   - Layer 2: Data Link Layer
#   - Layer 3: Network Layer
#   - Layer 4: Transport Layer

# =============================================================================


from config import SRC_PORT, DST_PORT, DATA_TYPE, DEFAULT_TTL, PROTOCOL_UDP, ETHER_TYPE_IPV4


# =============================================================================
# Layer 2 - Ethernet-like Frame
# =============================================================================

class Layer2_Frame: 
    """
    Represents a Data Link Layer frame (like an Ethernet frame)

    Fields:
        dst_mac    : 6 bytes    -- where this frame is going (next hop on this link)
        src_mac    : 6 bytes    -- who sent this frame
        frame_type : 2 bytes    -- 0x0800 = IPv4 payload
        payload    : variable   -- a Layer3_Packet object
    """

    # Fixed header size in bytes: 
    #   6 (dst) + 6 (src) + 2 (type) = 14 bytes
    HEADER_SIZE = 14 

    def __init__(self, dst_mac: str, src_mac: str, payload, frame_type: int = ETHER_TYPE_IPV4):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.frame_type = frame_type
        self.payload = payload      # Encapsulates Layer 3 packet into a frame before transmission

    def total_size(self) -> int:
        """Returns total frame size in bytes (header + payload)"""
        return self.HEADER_SIZE + self.payload.total_size()


# =============================================================================
# Layer 3 - IP-like Packet
# =============================================================================
class Layer3_Packet: 
    """
    Represents a Network Layer packet (like an IPv4 packet)

    Fields:
        src_ip    : 4 bytes   -- the original sender's IP
        dst_ip    : 4 bytes   -- the final destination's IP
        ttl       : 1 byte    -- Time To Live; decremented at every router
        protocol  : 1 byte    -- 17 = UDP payload
        total_length : 2 bytes   -- total packet size (header + payload) in bytes
        payload   : variable  -- a Layer4_Segment object
    """

    # Fixed header size in bytes: 
    #   4 (src_ip) + 4 (dst_ip) + 1 (ttl) + 1 (protocol) + 2 (total_length) = 12 bytes
    HEADER_SIZE = 12 

    def __init__(self, src_ip: str, dst_ip: str, payload, ttl: int = DEFAULT_TTL, protocol: int = PROTOCOL_UDP):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.payload = payload      # Encapsulates Layer 4 segment into IP-like packet before transmission
        self.total_length = self.total_size()

    def total_size(self) -> int:
        """Returns total packet size in bytes (header + payload)."""
        return self.HEADER_SIZE + self.payload.total_size()


# =============================================================================
# Layer 4 - UDP-like Segment with ACK support (rdt2.2)
# ============================================================================= 
class Layer4_Segment: 
    """
    Represents a Transport Layer segment (like a UDP segment, extended with
    sequence numbers and ACK support to implement rdt2.2)

    Fields:
        src_port : 2 bytes  -- sending application's port number
        dst_port : 2 bytes  -- receiving application's port number
        length   : 2 bytes  -- total segment size (header + data) in bytes
        checksum : 2 bytes  -- computed error detection value
        seg_type : 1 byte   -- 0 = DATA_TYPE segment, 1 = ACK_TYPE segment
        seq_num  : 1 byte   -- sequence number (0 or 1, alternating)
        data     : variable -- the application message bytes (empty for ACKs)
    """

    # Fixed header size in bytes: 
    #   2 (src_port) + 2 (dst_port) + 2 (length) + 2 (checksum) + 1 (seg_type) + 1 (seq_num) = 10 bytes
    HEADER_SIZE = 10 

    def __init__(self, src_port: int, dst_port: int, seg_type: int,
                 seq_num: int, data: bytes = b"", checksum: int = None):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seg_type = seg_type
        self.seq_num = seq_num
        self.data = data    # Encapsulates application data into UDP-like segment before transmission (bytes object)
        self.checksum = self.compute_checksum()
        self.length = self.total_size()

    def compute_checksum(self) -> int: 
        """
        Computes 16-bit (2 bytes) checksum over the segment's data bytes
        """
        # Build the segment as bytes
        segment = (
            self.src_port.to_bytes(2, 'big') +
            self.dst_port.to_bytes(2, 'big') +
            self.length.to_bytes(2, 'big') +
            (0).to_bytes(2, 'big') +    # checksum field temporarily zero, will be replaced by computed checksum 
            bytes([self.seg_type]) +
            bytes([self.seq_num]) +
            self.data
        )

    def is_valid(self):
        return self.checksum == self.compute_checksum()
    
    def total_size(self) -> int:
        """Returns total segment size in bytes (header + data)"""
        return self.HEADER_SIZE + len(self.data)

