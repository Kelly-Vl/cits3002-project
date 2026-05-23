# Contains header definisitions and classes for Layers 2,3, and 4

from config import SRC_PORT, DST_PORT, DATA_TYPE, DEFAULT_TTL, PROTOCOL_UDP, ETHER_TYPE_IPV4

class Segment: 
    ## Layer 4 - Transport Layer
    HEADER_SIZE = 10 

    def __init__(self, data, src_port = SRC_PORT, dst_port = DST_PORT, seg_type = DATA_TYPE, seq_num = 0):
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = len(data) + self.HEADER_SIZE 
        self.checksum = self.compute_checksum() 
        self.seg_type = seg_type
        self.seq_num = seq_num
        self.data = data

    def compute_checksum(self): 
        text = f"{self.src_port}{self.dst_port}{self.length}{self.seg_type}{self.seq_num}{self.data}"
        total = 0
        for ch in text: 
            total += ord(ch)
        checksum = total & 256

        return checksum

    def validity(self):
        return self.checksum == self.compute_checksum()

        
class Packet: 
    ## Layer 3 - Network Layer
    HEADER_SIZE = 12 

    def __init__(self, src_ip, dst_ip, payload, ttl = DEFAULT_TTL, protocol = PROTOCOL_UDP):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.length = payload.length + self.HEADER_SIZE
        self.payload = payload

class Frame: 
    ## Layer 2 - Data Link Layer
    def __init__(self, dst_mac, src_mac, payload, frame_type=ETHER_TYPE_IPV4):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.frame_type = frame_type
        self.payload = payload