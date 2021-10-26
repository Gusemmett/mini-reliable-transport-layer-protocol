# Author Angus Emmett
# CS60 lab3

import socket
from queue import Queue
from threading import Thread
from common import *
import time


SERVER = 'localhost'
PORT = 60001

class MRT_server():
	
	def __init__(self, server, port):
		self.BUFSIZE = 1024
		self.MAX_BUFSIZE = 1000

		# Setting up socket to listen 
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.bind((server,port))

		self.packet_buffer = Queue()
		self.clients_data = {}

		# Thread for recieving acks from server
		rec = Thread(target=self.server_recv_data).start()

		# Thread for sending data packets
		snd = Thread(target=self.server_send_data).start()


	def combine_packets(self, packets):
		# Sort packets by seq_num
		packets = sorted(packets, key=compare_packets)
		#Check if any packets are missing
		missing_seq_nums = []
		prev_seq_num = byte_to_int(parse_header(packets[0])["seq_num"])
		for x in packets[1:]:
			curr_seq_num = byte_to_int(parse_header(x)["seq_num"])
			if prev_seq_num + 1 != curr_seq_num:
				for i in range(prev_seq_num + 1, curr_seq_num):
					missing_seq_nums.append(i)
			prev_seq_num = curr_seq_num

		out_data = bytearray()
		if len(missing_seq_nums) == 0:
			for x in packets:
				out_data = out_data + parse_data(x)

		return out_data, missing_seq_nums


	def mrt_accept(self, addr):
		p_strt = build_header(self.soc.getsockname()[1], addr[1], strt=1)
		self.soc.sendto(p_strt, addr)
	

	def mrt_receive(self, addr, data, header):
		# If checksum is not valid dont send any ack and wait for retransmission
		if is_valid_checksum(data):
			#Congestion handled with ternary operator 
			p_ack = build_header(self.soc.getsockname()[1], addr[1], ack_from=byte_to_int(header['seq_num']), congestion= 0 if (self.packet_buffer.qsize() < self.MAX_BUFSIZE) else 1)
			#Adding data to clients packet list
			self.clients_data[addr[1]].append(data)
			#Sending ACK
			self.soc.sendto(p_ack, addr)


	def mrt_close(self, addr):
		# TODO check for missing packets
		p_fin = build_header(self.soc.getsockname()[1], addr[1], fin=1)
		self.soc.sendto(p_fin, addr)


	def server_recv_data(self):
		while True:
			data,addr = self.soc.recvfrom(self.BUFSIZE)
			data = bytearray(data)
			self.packet_buffer.put((data,addr))

	def server_send_data(self):
		
		while True:
			data, addr = self.packet_buffer.get(block=True)
			header = parse_header(data)

			# New client is trying to connect
			if is_start_packet(header):
				self.clients_data[addr[1]] = []
				self.mrt_accept(addr)

			# Packet is a data packet
			if is_data_packet(data):
				self.mrt_receive(addr, data, header)

			# Printing data to stdout
			if is_fin_data_packet(header):
				combined_data, missing_packets = self.combine_packets(self.clients_data[addr[1]])
				if len(missing_packets) == 0:
					print(combined_data.decode("utf-8"))
				else:
					print("Data Currupted")

			# Client is stopping connection
			if is_fin_packet(header):
				self.mrt_close(addr)


if __name__ == "__main__":
	server = MRT_server(SERVER, PORT)