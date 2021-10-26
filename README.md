# MRT (Mini Reliable Transport)
## Angus Emmett

## General
This repo implements a mini reliable transport layer protocol similar to TCP. I built MRT on top of UDP however I do not use UDP's checksum feature as I implement that myself. The goals of MRT for building MRT were:

1. Protection against packet loss ☑️
2. The abilty to detect packet corruption and retransmit the packet ☑️
3. Packets can arrive out of order ☑️
4. Fast transmission when latency is low and high ☑️ 
5. Can handle large data ☑️
6. Flow Control ☑️


## Packet Implementation
### Header
The header consists of 24 bytes, with the division of bytes layedout as follows:
* ```src_port``` __2 bytes__
	* The source port of the sender
* ```dst_port``` __2 bytes__
	* The port of the reciever
* ```seqNum``` __4 bytes__
	* The sequence number of the packet, will start a random number for the first packet and increase incrementally with each subsequent packet
* ```ackNumFrom``` __4 bytes__
	* The ackknowlegement field that sends back the seq_number to acknowledge reciept
* ```ackNumTo```  __4 bytes__
* ```congestion``` __2 bytes__
	* Congestion control: 
		* 0: proceed as normal 
		* 1: Reduce window size to 1 
* ```length``` __2 bytes__
	* Length of the data portion of the packet
* ```strt``` __1 byte__
	* Field to indicate a connection to be created
	* Anything but 0 indicates a start
* ```fin``` __1 byte__
	* Field to indicate to close a connection
	* 1 requests to close connection
	* 255 indicate finished data transfer
* ```checksum``` __2 bytes__
	* Holds the value of the checksum for the data

Total Header Size = 24 bytes

### Data
The max data size for a packet is 1000 bytes and the minimum is 0 bytes, this means that the maximum size a packet (including the header) is 1024 bytes (2^10) and the minimum size is 24 bytes.