# Implements Host and Router classes

from config import * 
from protocol import Segment, Packet, Frame

## shared dictionary so that router can deliver frames from A to B
NETWORK_DEVICES = {} 

## helper function for /24 routing 
## let's us check if 10.0.2.20 belongs to 10.0.2.0/24
def ip_in_network(ip, network):
    network_ip, mask = network.split("/")
    mask = int(mask)

    ip_parts = ip.split(".")
    network_parts = network_ip.split(".")

    if mask == 24:
        return ip_parts[:3] == network_parts[:3]
    
    return False

class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = routing_table
        self.arp_table = arp_table

        self.seq_num = 0       ## DATA sequence number this host will send next
        self.expected_seq = 0  ## DATA sequence number this host expects to receive 
        self.last_ack_seq = 1  ## for when receiving duplicate or corrupted data

    def lookup_route(self, dst_ip):
        ## checks routing table first for local network & default route
        for network, route in self.routing_table.items():
            if network != "0.0.0.0" and ip_in_network(dst_ip, network):
                return route
        
        return self.routing_table["0.0.0.0"]
    
    def send_data(self, data, dst_ip, router):
        ## host sends application data to layer 4 (Transport Layer)

        ## segmentation into 500-byte chunks
        ## MAX_SEGMENT_SIZE = 500 already set in config.py
        chunks = [
            data[i:i + MAX_SEGMENT_SIZE]
            for i in range(0, len(data), MAX_SEGMENT_SIZE)
        ]

        for chunk in chunks:
            print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(chunk)}")

            ack_received = False

            ## DATA segment creation
            while not ack_received:
                segment = Segment(
                    src_port=SRC_PORT,
                    dst_port=DST_PORT,
                    seg_type=DATA_TYPE,
                    seq_num=self.seq_num,
                    data=chunk
                )

                print(f"{self.name}: Layer 4: Checksum computed")
                print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.seq_num}) (encapsulation)")
                print(f"{self.name}: Layer 4: Segment sent to Network Layer")

                ## waiting for ACK before sending next chunk
                ack_received = self.send_segment(segment, dst_ip, router)

                if not ack_received:
                    print(f"{self.name}: Layer 4: Segment retransmitted due to incorrect ACK")

    def send_segment(self, segment, dst_ip, router):
        ## host sends segment to Layer 3 (Network Layer)
        print(f"{self.name}: Layer 3: Segment received from Transport Layer")
        
        ## encapsulates Segment --> Packet
        packet = Packet(
            src_ip=self.ip,
            dst_ip=dst_ip,
            payload=segment
        )

        print(f"{self.name}: Layer 3: Packet created: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")

        ## decides the next-hop IP 
        route = self.lookup_route(dst_ip)
        next_hop_ip = route[0]

        if next_hop_ip == self.ip:
            next_hop_ip = dst_ip
        
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        return self.send_packet(packet, next_hop_ip, router)

    def send_packet(self, packet, next_hop_ip, router):
        ## host sends packet to Layer 2 (Data Link Layer)
        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        ## uses the ARP table to find the next-hop MAC address 
        ## ARP table maps next-hop IPs to MAC addresses
        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) --> {dst_mac}")

        ## encapsulates Packet --> Frame
        frame = Frame(
            src_mac=self.mac,
            dst_mac=dst_mac,
            payload=packet
        )

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")

        return router.receive_frame(frame, self)

    def receive_frame(self, frame, sender):
        ## host receives frame from Layer 2 (Data Link Layer)
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        packet = frame.payload

        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        ## checks if the packet is actually meant for this host or not
        if packet.dst_ip != self.ip:
            print(f"{self.name}: Layer 3: Packet dropped because destination IP does not match local host")
            return False
        
        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")

        return self.receive_segment(packet.payload, packet.src_ip, sender)
    
    def receive_segment(self, segment, src_ip, router):
        ## host receives segment from Layer 3 (Network Layer)
        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        ## main rdt2.2 logic
        ## 1. verify checksum
        if not segment.verify_checksum():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")

            ack = Segment(
                src_port=DST_PORT,
                dst_port=SRC_PORT,
                seg_type=ACK_TYPE,
                seq_num=self.last_ack_seq,
                data=b""
            )

            print(f"{self.name}: Layer 4: ACK sent: seq={self.last_ack_seq}")
            self.send_segment(ack, src_ip, router)
            return False

        print(f"{self.name}: Layer 4: Checksum verified")

        ## 2. deliver valid DATA 
        if segment.seg_type == DATA_TYPE:
            if segment.seq_num == self.expected_seq:
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")

                self.last_ack_seq = segment.seq_num
                self.expected_seq = 1 - self.expected_seq
                ack_seq = segment.seq_num
            else:
                print(f"{self.name}: Layer 4: Duplicate DATA segment detected")
                print(f"{self.name}: Layer 4: Re-sending last ACK")
                ack_seq = self.last_ack_seq

            ## 3. send ACK
            ack = Segment(
                src_port=DST_PORT,
                dst_port=SRC_PORT,
                seg_type=ACK_TYPE,
                seq_num=ack_seq,
                data=b""
            )

            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ack_seq})")
            print(f"{self.name}: Layer 4: ACK sent: seq={ack_seq}")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            return self.send_segment(ack, src_ip, router)
        
        ## 4. flip sequence number only after correct ACK 
        elif segment.seg_type == ACK_TYPE:
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")

            if segment.seq_num == self.seq_num:
                self.seq_num = 1 - self.seq_num
                return True

            print(f"{self.name}: Layer 4: Incorrect or duplicate ACK received")
            return False
        
