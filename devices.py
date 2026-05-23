# Implements Host and Router classes

from config import * 
from protocol import Segment, Packet, Frame

class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = routing_table
        self.arp_table = arp_table
        self.seq_num = 0
    
    def send_data(self, data, dst_ip, router):
        chunks = [
        data[i:i + MAX_SEGMENT_SIZE]
        for i in range(0, len(data), MAX_SEGMENT_SIZE)
        ]

        for chunk in chunks:
            print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(chunk)}")

            segment = Segment(
            data=chunk,
            src_port=SRC_PORT,
            dst_port=DST_PORT,
            seg_type=DATA_TYPE,
            seq_num=self.seq_num
        )

            print(f"{self.name}: Layer 4: Checksum computed")
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.seq_num}) (encapsulation)")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            self.send_segment(segment, dst_ip, router)

    def send_segment(self, segment, dst_ip, router):
        packet = Packet(
            src_ip=self.ip,
            dst_ip=dst_ip,
            payload=segment
        )

        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        route = self.routing_table["0.0.0.0"]
        next_hop_ip = route[0]

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        self.send_packet(packet, next_hop_ip, router)
    
    def send_packet(self, packet, next_hop_ip, router):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        frame = Frame(
            src_mac=self.mac,
            dst_mac=dst_mac,
            payload=packet
        )

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")

        router.receive_frame(frame, self)

    def receive_frame(self, frame, sender):
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        packet = frame.payload

        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")

        self.receive_segment(packet.payload, packet.src_ip, sender)

    def receive_segment(self, segment, src_ip, router):
        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if not segment.is_valid():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")
            return
        
        print(f"{self.name}: Layer 4: Checksum verified")

        if segment.seg_type == DATA_TYPE: 
            print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")

            ack = Segment(
                data="",
                src_port=DST_PORT,
                dst_port=SRC_PORT, 
                seg_type=ACK_TYPE,
                seq_num=segment.seq_num
            )

            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num})")
            print(f"{self.name}: Layer 4: ACK sent: seq={segment.seq_num}")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            self.send_segment(ack, src_ip, router)
        
        elif segment.seg_type == ACK_TYPE: 
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
            self.seq_num = 1 - self.seq_num
    
    
class Router:
    def __init__(self, name, routing_table, arp_table):
        self.name = name
        self.routing_table = routing_table
        self.arp_table = arp_table

    def receive_frame(self, frame, sender):
        packet = frame.payload

        if frame.dst_mac == R1_INTERFACE_1_MAC: 
            incoming_interface = "Interface 1"
        else:
            incoming_interface = "Interface 2"
        
        print(f"{self.name}: Layer 2: Frame received on {incoming_interface}")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {incoming_interface}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        old_ttl = packet.ttl
        packet.ttl -= 1

        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} → {packet.ttl}")

        if packet.ttl <= 0:
            print(f"{self.name}: Layer 3: Packet dropped due to TTL expiry")
            return
        
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        if packet.dst_ip.startswith("10.0.1."):
            interface_name = "Interface 1"
            src_mac = R1_INTERFACE_1_MAC
        else:
            interface_name = "Interface 2"
            src_mac = R1_INTERFACE_2_MAC

        next_hop_ip = packet.dst_ip

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected ({interface_name})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        new_frame = Frame(
            src_mac=src_mac,
            dst_mac=dst_mac,
            payload=packet
        )

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {interface_name}")

        if packet.dst_ip == HOST_A_IP:
            NETWORK_DEVICES["Host A"].receive_frame(new_frame, self)
        elif packet.dst_ip == HOST_B_IP:
            NETWORK_DEVICES["Host B"].receive_frame(new_frame, self)



NETWORK_DEVICES = {}
