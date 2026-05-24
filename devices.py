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

## HOST class as blueprints to simulate Host A and Host B
class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = routing_table
        self.arp_table = arp_table

        self.seq_num = 0          ## DATA sequence number this host will send next
        self.expected_seq = 0     ## DATA sequence number this host expects to receive 
        self.last_ack_seq = None  ## for when receiving duplicate or corrupted data

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
            ack_received = False

            ## DATA segment creation
            while not ack_received:
                print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(chunk)}")
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
                print("\n")

                ## waiting for ACK before sending next chunk
                ack_received = self.send_segment(segment, dst_ip, router)

                if not ack_received:
                    print(f"{self.name}: Layer 4: Segment retransmitted due to incorrect ACK")

    def send_segment(self, segment, dst_ip, router):
        ## host sends segment to Layer 3 (Network Layer)

        ## encapsulates Segment --> Packet
        packet = Packet(
            src_ip=self.ip,
            dst_ip=dst_ip,
            payload=segment
        )

        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={packet.ttl}")
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
        print("\n")

        return self.send_packet(packet, next_hop_ip, router)

    def send_packet(self, packet, next_hop_ip, router):
        ## host sends packet to Layer 2 (Data Link Layer)
        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        ## uses the ARP table to find the next-hop MAC address 
        ## ARP table maps next-hop IPs to MAC addresses
        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        ## encapsulates Packet --> Frame
        frame = Frame(
            src_mac=self.mac,
            dst_mac=dst_mac,
            payload=packet
        )

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")
        print("\n")

        return router.receive_frame(frame, self)

    def receive_frame(self, frame, sender):
        ## host receives frame from Layer 2 (Data Link Layer)
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        print("\n")

        packet = frame.payload

        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        ## checks if the packet is actually meant for this host or not
        if packet.dst_ip != self.ip:
            print(f"{self.name}: Layer 3: Packet dropped because destination IP does not match local host")
            return False
        
        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
        print("\n")

        return self.receive_segment(packet.payload, packet.src_ip, sender)
    
    def receive_segment(self, segment, src_ip, router):
        ## host receives segment from Layer 3 (Network Layer)
        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        ## main rdt2.2 logic
        ## 1. verify checksum
        if not segment.verify_checksum():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")

            ## only re-send a previous ACK if we've actually sent one before
            ## once a valid DATA segment has been received and ACK'd, 
            ## the guard passes and re-sending works correctly for all subsequent corruption cases
            if self.last_ack_seq is not None:
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
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
            print("\n")

            return self.send_segment(ack, src_ip, router)
        
        ## 4. flip sequence number only after correct ACK 
        elif segment.seg_type == ACK_TYPE:
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
            print("\n")

            if segment.seq_num == self.seq_num:
                self.seq_num = 1 - self.seq_num
                return True

            print(f"{self.name}: Layer 4: Incorrect or duplicate ACK received")
            print("\n")
            return False
        


## ROUTER class as blueprints to simulate Router (R1)
class Router:
    def __init__(self, name, routing_table, arp_table):
        self.name = name
        self.routing_table = routing_table
        self.arp_table = arp_table
        self.mac_learning_table = {} ## learned MAC addresses 

    def lookup_route(self, dst_ip): 
        ## checks which network the destination IP belongs to
        for network, route in self.routing_table.items():
            if ip_in_network(dst_ip, network):
                return route
            
        return None
    
    def receive_frame(self, frame, sender):
        ## extracts packet from frame; removes Layer 2 encapsulation
        packet = frame.payload

        ## determine incoming interface
        ## the destination MAC tells the router which interface received the frame
        incoming_iface = R1_MAC_TO_IFACE.get(frame.dst_mac)
        if incoming_iface is None:
            print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match router")
            return False
        
        incoming_interface = "Interface 1" if incoming_iface == "eth0" else "Interface 2"

        ## determine incoming interface
        ## the destination MAC tells the router which interface received the frame
        # if frame.dst_mac == R1_INTERFACE_1_MAC:
        #     incoming_interface = "Interface 1"
        # elif frame.dst_mac == R1_INTERFACE_2_MAC:
        #     incoming_interface = "Interface 2"
        # else:
        #     ## prevents router from assuming every non-Interface-1 frame belongs to Interface 2 
        #     print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match router")
        #     return False

        ## Layer 2 logging 
        print(f"{self.name}: Layer 2: Frame received on {incoming_interface}")

        ## simulates router MAC learning 
        self.mac_learning_table[frame.src_mac] = incoming_interface
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {incoming_interface}")

        ## deliver packet to Layer 3, finished in Layer 2
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        print("\n")

        ## read packet header & destination IP to decide where to forward packet next
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        ## every router hop reduces TTL 
        old_ttl = packet.ttl
        packet.ttl -= 1

        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} → {packet.ttl}")

        ## TTL expiry check to prevent infinite routing loops 
        if packet.ttl <= 0:
            print(f"{self.name}: Layer 3: Packet dropped due to TTL expiry")
            return False
        
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        ## routing table lookup, checks ROUTING_TABLE_R1 from config.py
        route = self.lookup_route(packet.dst_ip)

        ## simulates unreachable network
        if route is None:
            print(f"{self.name}: Layer 3: Packet dropped because no route was found")
            return False
        
        ## extracting routing decision
        next_hop_ip, outgoing_interface = route

        ## choose source MAC 
        ## router creates a new Layer 2 frame so source & destination MAC changes
        ## however, IP addresses stay the same
        if next_hop_ip in [HOST_A_IP, HOST_B_IP]:
            next_hop_ip = packet.dst_ip

        interface_name = "Interface 1" if outgoing_interface == "eth0" else "Interface 2"
        src_mac = R1_INTERFACE_TO_MAC[outgoing_interface]

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected ({interface_name})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        print("\n")

        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        ## find destination MAC using the ARP table
        if next_hop_ip not in self.arp_table:
            ## prevents KeyError if the ARP is missing an entry 
            print(f"{self.name}: Layer 2: Frame dropped because no MAC address was found for next-hop IP {next_hop_ip}")
            return False

        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        ## create a new frame for re-encapsulation (packet --> new Layer 2 frame)
        new_frame = Frame(
            src_mac=src_mac,
            dst_mac=dst_mac,
            payload=packet
        )

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {interface_name}")
        print("\n")

        ## simulates physical delivery 
        ## router sends frame out interface, host receives frame 
        if packet.dst_ip == HOST_A_IP:
            return NETWORK_DEVICES["Host A"].receive_frame(new_frame, self)

        if packet.dst_ip == HOST_B_IP:
            return NETWORK_DEVICES["Host B"].receive_frame(new_frame, self)

        return False