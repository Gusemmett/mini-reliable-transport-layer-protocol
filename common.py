# Author: Angus Emmett
# CS60 lab3

from collections import deque
from random import randint
from math import ceil

##### parse_header ######
# Function that parses the header from a packet
# Input: 
# 		- packet: bytearray - must be at least 24 bytes
# Output:
# 		- dictionary: {key:bytearray}
def parse_header(packet):
	if type(packet) != bytearray:
		raise TypeError("Must be bytearray")
	if len(packet) < 24:
		raise ValueError("Bytearray must be >= 24 bytes")
		
	packet = packet[:24]

	out = {
		"src_port": 	packet[0:2],
		"dst_port": 	packet[2:4],
		"seq_num": 		packet[4:8],
		"ack_from": 	packet[8:12],
		"ack_to":		packet[12:16],
		"congestion": 	packet[16:18],
		"length": 		packet[18:20],
		"strt":			packet[20:21],
		"fin": 			packet[21:22],
		"checksum": 	packet[22:24]}

	return out


def parse_data(packet):
	return packet[24:]

##### build_header ######
# Function that builds the header described in the README
# Input: 
# 		- all inputs need to be of type int
def build_header(src_port, dst_port, seq_num=0, ack_from=0, ack_to=0, congestion=0, length=0, strt=0, fin=0, checksum=0):
	header = bytearray(24)
	header[0:2] 	= src_port.to_bytes(2,"big")
	header[2:4] 	= dst_port.to_bytes(2,"big")
	header[4:8] 	= seq_num.to_bytes(4,"big")
	header[8:12] 	= ack_from.to_bytes(4,"big")
	header[12:16] 	= ack_to.to_bytes(4,"big")
	header[16:18]	= congestion.to_bytes(2,"big")
	header[18:20]	= length.to_bytes(2,"big")
	header[20:21]	= strt.to_bytes(1,"big")
	header[21:22]	= fin.to_bytes(1,"big")
	header[22:24]	= checksum.to_bytes(2,"big")

	return header


#### packeterize_data ####
# Function that returns a list of bytearrays with 
# each item represeting a packet described in the README
# Input
# 		- data: bytearray
# 		- src_port & dst_port: int
def packeterize_data(data, src_port, dst_port, DATA_PACKET_SIZE=1000):
	data_len = len(data)
	packets = deque()
	random_start = randint(0,1000000000)

	for i in range(ceil(data_len / DATA_PACKET_SIZE)):
		seq_num = random_start + i
		start_i = i * DATA_PACKET_SIZE

		if (data_len > start_i + DATA_PACKET_SIZE):
			p_data = data[start_i : start_i + DATA_PACKET_SIZE]
		else: 
			p_data = data[start_i : data_len]
		
		# Creating the header
		header = build_header(src_port=src_port, dst_port=dst_port, seq_num=seq_num, length=len(p_data), checksum=calc_checksum(p_data))  
		packets.appendleft(header + p_data)

	return packets



#### is_start_packet ####
def is_start_packet(header):
	if byte_to_int(header['strt']): 
		return True
	else:
		return False

#### is_fin_packet ####
def is_fin_packet(header):
	if byte_to_int(header['fin']) != 0 and byte_to_int(header['fin']) != 255: 
		return True
	else:
		return False

def is_fin_data_packet(header):
	if byte_to_int(header['fin']) == 255: 
		return True
	else:
		return False

#### is_data_packet ####
def is_data_packet(packet):
	header = parse_header(packet)
	if byte_to_int(header['seq_num']):
		return True
	else:
		return False

#### is_congested ####
def is_congested(header):
	if byte_to_int(header['congestion']):
		return True
	else:
		return False

#### byte_to_int ####
def byte_to_int(bytearr):
	return int.from_bytes(bytearr, byteorder='big', signed=False)


#### compare_packets ####
def compare_packets(p1):
	p1h = parse_header(p1)
	return byte_to_int(p1h["seq_num"])


#### calc_checksum ####
def calc_checksum(data):
	sm = 0
	for x in data:
		sm += x
	return sm % 60000

#### check_checksum ####
def is_valid_checksum(packet):
	header = parse_header(packet)
	cs = byte_to_int(header["checksum"])

	if cs == calc_checksum(parse_data(packet)):
		return True
	else:
		return False



if __name__ == '__main__':
	byte_test = bytearray([x for x in range(0,24)])
	print(parse_header(byte_test))

