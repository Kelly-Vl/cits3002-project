## protocol.py

"""
Defines the data structures (header definitions and classes) for each layer:
- Layer 2: Data Link Layer
- Layer 3: Network Layer
- Layer 4: Transport Layer
"""

from config import *

## Layer 2 - Ethernet-like Frame
class Frame: 
    """
    Represents a Data Link Layer frame (like an Ethernet frame)

    Fields:
        dst_mac: 6 bytes
        src_mac: 6 bytes
        frame_type: 2 bytes - 0x0800 = IPv4 payload
        payload: variable - a Packet object
    """

    ## Fixed header size: 6 (dst) + 6 (src) + 2 (type) = 14 bytes
    HEADER_SIZE = 14 

    def __init__(self, dst_mac, src_mac, payload, frame_type = ETHER_TYPE_IPV4):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.frame_type = frame_type
        self.payload = payload ## Encapsulates Layer 3 packet into a frame before transmission

    def total_size(self):
        ## Returns total frame size in bytes (header + payload) 
        return self.HEADER_SIZE + self.payload.total_size()


## Layer 3 - IP-like Packet
class Packet: 
    """
    Represents a Network Layer packet (like an IPv4 packet)

    Fields:
        src_ip: 4 bytes
        dst_ip: 4 bytes
        ttl: 1 byte - Time To Live; decremented at every router
        protocol: 1 byte - 17 = UDP payload
        total_length: 2 bytes - total packet size (header + payload) in bytes
        payload: variable - a Layer4_Segment object
    """

    ## Fixed header size: 4 (src_ip) + 4 (dst_ip) + 1 (ttl) + 1 (protocol) + 2 (total_length) = 12 bytes
    HEADER_SIZE = 12 

    def __init__(self, src_ip, dst_ip, payload, ttl = DEFAULT_TTL, protocol = PROTOCOL_UDP):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.payload = payload  ## Encapsulates Layer 4 segment into IP-like packet before transmission
        self.total_length = self.total_size()

    def total_size(self):
        ## Returns total packet size in bytes (header + payload)
        return self.HEADER_SIZE + self.payload.total_size()

## Layer 4 - UDP-like Segment with ACK support (rdt2.2)
class Segment: 
    """
    Represents a Transport Layer segment (like a UDP segment, with
    sequence numbers and ACK support to implement rdt2.2)

    Fields:
        src_port: 2 bytes
        dst_port: 2 bytes
        length: 2 bytes - total segment size (header + data) in bytes
        checksum: 2 bytes - computed error detection value
        seg_type: 1 byte - 0 = DATA_TYPE segment, 1 = ACK_TYPE segment
        seq_num: 1 byte - sequence number (0 or 1)
        data: variable- the application message bytes (empty for ACKs)
    """

    ## Fixed header size: 2 (src_port) + 2 (dst_port) + 2 (length) + 2 (checksum) + 1 (seg_type) + 1 (seq_num) = 10 bytes
    HEADER_SIZE = 10 

    def __init__(self, src_port, dst_port, seg_type, seq_num, data = b"", checksum = None):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seg_type = seg_type
        self.seq_num = seq_num
        self.data = data  ## Encapsulates application data into UDP-like segment before transmission (bytes object)
        self.length = self.total_size()
        self.checksum = checksum if checksum is not None else self.compute_checksum()

    def compute_checksum(self): 
        ## Build the segment as bytes
        segment = (
            self.src_port.to_bytes(2, 'big') +
            self.dst_port.to_bytes(2, 'big') +
            self.length.to_bytes(2, 'big') +
            (0).to_bytes(2, 'big') + ## checksum field temporarily zero, will be replaced by computed checksum 
            self.seg_type.to_bytes(1, 'big') +
            self.seq_num.to_bytes(1, 'big') +
            self.data
        )

        ## Pad if odd byte length
        if len(segment) % 2 != 0:
            segment += b"\x00"

        total = 0

        ## Process into 16-bit words (2 bytes at a time)
        for i in range(0, len(segment), 2):
            total += (segment[i] << 8) + segment[i+1]

        # Wrap carry bits
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)

        ## One's complement (flip all the bits)
        checksum = ~total & 0xFFFF

        return checksum

    def verify_checksum(self):
        return self.checksum == self.compute_checksum()
    
    def total_size(self) -> int:
        ## Returns total segment size in bytes (header + data)
        return self.HEADER_SIZE + len(self.data)

