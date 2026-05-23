# Main entry file
# The only file called for execution

import sys

from config import * 
from devices import * 

def main():
    # Error handling: Incorrect input size
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        return
    
    # Get the command-line arguments
    try:
        message_size = int(sys.argv[1])

    # Error handling: Incorrect input type 
    except ValueError:
        print("Error: message_size must be an integer")
        return
    
    # Error handling: Must send non-negative size
    if message_size < 0:
        print("Error: message_size must be 0 or greater")
        return
    
    # Create the simulated Hosts (Host A and Host B)
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

    # Create the simulated Router R1
    router = Router(
        name="Router R1",
        routing_table=ROUTING_TABLE_R1,
        arp_table=ARP_TABLE_R1
    )

    # Store devices globally (so they can access each other during simulation)
    NETWORK_DEVICES["Host A"] = host_a
    NETWORK_DEVICES["Host B"] = host_b
    NETWORK_DEVICES["Router R1"] = router

    # Create data payload (message of "X" characters)
    data = "X" * message_size

    # Sending data from Host A to Host B
    host_a.send_data(
        data=data,
        dst_ip=HOST_B_IP,
        router=router
    )


if __name__ == "__main__":
    main()