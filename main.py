# Main entry file
# The only file called for execution

import sys

from config import * 
from devices import * 

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        return
    
    try:
        message_size = int(sys.argv[1])
    except ValueError:
        print("Error: message_size must be an integer")
        return
    
    if message_size < 0:
        print("Error: message_size must be 0 or greater")
        return
    
    host_a = Host(
        name="Host A",
        ip=HOST_A_IP,
        mac=HOST_A_MAC,
        routing_table=ROUTING_TABLE_HOST_A,
        arp_table=ARP_TABLE_HOST_A
    )

    host_b = Host(
        name="Host B",
        ip=HOST_B_IP,
        mac=HOST_B_MAC,
        routing_table=ROUTING_TABLE_HOST_B,
        arp_table=ARP_TABLE_HOST_B
    )

    router = Router(
        name="Router R1",
        routing_table=ROUTING_TABLE_R1,
        arp_table=ARP_TABLE_R1
    )

    NETWORK_DEVICES["Host A"] = host_a
    NETWORK_DEVICES["Host B"] = host_b
    NETWORK_DEVICES["Router R1"] = router

    data = "X" * message_size

    host_a.send_data(
        data=data,
        dst_ip=HOST_B_IP,
        router=router
    )


if __name__ == "__main__":
    main()