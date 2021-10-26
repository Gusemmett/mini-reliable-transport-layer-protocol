# CS60 Spring 2021, Lab 3
## Angus Emmett
#### GitHub Username: gusemmett


<!-- ### protect agaisnt packet loss/ curruption (checksum) -- DONE
* send ack packets back to client for each packet recieved
* ACKs can be for multiple packets

### out of order delivery -- DONE
* send packets with int specifying the order and then put in place at the server side

### fast transmission -- DONE
* create sliding window imlpementation 
* slow start of the window and double every time (maybe?)

### various data size support -- DONE
* split data down into bytes of largest packet size 

### flow control -- DONE
* have flag in the acks about if buffer is conjested

### server handles multiple clients -- DONE
* threading -- easy -->


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


## Code Implementation

### Client.py
#### General
This file serves as the sender and accepts anytype of data to send to the server. However the server will output to stdout so sending a string encoded in UTF-8 will make sure the output on the server side is correct.

It is implemented as a Python class called ```MRT_client```

#### Use
A general use case would be as follows
```py
client = MRT_client() 			# Inits the client
client.mrt_connect(SERVER, S_PORT)	# Connects to the server on the provided server and port
client.mrt_send(data) 			# Sends the data to the server
client.mrt_disconnect()			# Disconnects from the server
client.mrt_close()			# Closes the socket
```

#### Flow
* The client starts off by trying to connect to the server and will loop forever until it connect to a server
* Once connected and the user calls ```client.mrt_send(data)``` the client will convert the data into packets and then send off each packet
* There are 3 threads used in this client 
	* Send Thread: Looks at the to_send buffer and will send a new packet as long as the sliding window permits. And then adds this packet to another buffer that keeps track of packets that have been sent but have not recieved an ACK for (```sent_no_ack```). The time is also tracked when each packet is sent.
	* Check retransmission thread: Every couple of seconds this thread checks the ```sent_no_ack``` buffer to check if any packets have timed out and if any have it will remove the packer from this buffer and add it back to the ```to_send``` buffer
	* Recv Thread: This thread recieves ACKs from the server and will remove the packets from the ```sent_no_ack``` buffer as their ACKs have now been obtained.
* Sliding window implementation
	* The client will slowly double the size of the window until it reaches a ```MAX_WINDOW_VALUE``` and hold its window size there
	* When the client recieves a congestion warning in an ack it reduces its window size to 1
* When the client wants to disconnets it sends a fin packet to the server and then server responds with also a fin packet thus the connect is terminated
* When packet gets build checksum is calculated and added to the header


### Server.py
#### General
This file serves as the reciever and will accept any client that follows the above protocol. The server accepts anytype of data but it will print it out to stdout (as per the specs) thus string encoded data is best. The server will also run forever or until stopped by pressing ```control + C```.

The server is implemented as a python class called ```MRT_server```

#### Use
One simple command opens the server and allows for connections:
```py
server = MRT_server(SERVER, PORT)
```
#### Flow
* The server starts by preparing its sockets for connections by clients.
* When a client connects there is a recieve thread that just pusts the incoming packet in a buffer
* Then there is a processing thread that gets the next packet out of the buffer and processes it accordingly:
	* New client is trying to connect
	* Data recieved from a client
	* Finished data stream
	* Client wants to disconnect
* If the buffer gets too large the server will start sending back acks with congestion warnings which will ask the client to reduce its window size
* If the checksum fails then the server drops the package and waits for the resend
* When all the data has been delivered to the server it corrects the order of the packets and checks if any are missing, then outputs to the server or re-asks for the missing packets
* Can handle multiple clients on the same port


### Common.py
This file serves as a common library between the two above files.
The included functions are:

```py
def parse_header(packet)
def parse_data(packet)
def build_header(src_port, dst_port, seq_num=0, ack_from=0, ack_to=0, congestion=0, length=0, strt=0, fin=0, checksum=0)
def packeterize_data(data, src_port, dst_port, DATA_PACKET_SIZE=1000)
def is_start_packet(header)
def is_fin_packet(header)
def is_fin_data_packet(header)
def is_data_packet(packet)
def is_congested(header)
def byte_to_int(bytearr)
def compare_packets(p1)
def calc_checksum(data)
def is_valid_checksum(packet)
```
