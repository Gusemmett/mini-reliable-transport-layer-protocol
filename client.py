# Author Angus Emmett
# CS60 lab3

import socket
from common import *
from threading import Thread
import time

SERVER = 'localhost'
S_PORT = 60001



class MRT_client():

	def __init__(self):
		self.TIMEOUT = 5
		self.WINDOW_SIZE = 1
		self.soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		self.server_info = None
		self.src_port = None
		self.dst_port = None

		self.total_acks = 0
		self.sent_no_ack_tbl = {}
		self.to_send_buffer = None
		self.sent_final_ack = False



	#### mrt_connect ####
	# A function that starts the communication with the server
	def mrt_connect(self, server, port):

		# Setting up udp socket
		self.soc.connect((server, port))
		self.src_port = self.soc.getsockname()[1]
		self.dst_port = port
		

		# Getting client port and building start packet
		p_strt = build_header(123, port, strt=1)


		while True:
			try:
				#sending start packet and waiting for ack
				self.soc.sendall(p_strt)

				p_ack, address = self.soc.recvfrom(1024)
				p_ack = bytearray(p_ack)
			
				#Getting the info from the header
				self.server_info = parse_header(p_ack)
				break

			except Exception as e:
				time.sleep(2)
				print("Cannot connect to the server retrying in 5 seconds")
				time.sleep(5)
				print("Retrying ...")

		print("Connected to server")
		return

	#### stop_connection ####
	# A function to send a fin packet to the server to close the connection
	# Inputs:
	#			- soc: socket
	# 			- src_port & dst_port : int
	def mrt_disconnect(self):
		print("Disconnecting...")
		time.sleep(1)
		for _ in range(2):
			# Sending fin package 
			p_fin = build_header(self.src_port, self.dst_port, fin=1)
			self.soc.sendall(p_fin)

			try:
				# Waiting for ack of fin package back
				self.soc.settimeout(2)
				p_ack_fin, address = self.soc.recvfrom(1024)
				p_ack_fin = bytearray(p_ack_fin)
			
				if is_fin_packet(parse_header(p_ack_fin)):
					print("Server Connection Closed")
					return True
			except:
				print("Same err")
				continue

		print("Server Connection Closed")
		return False


	def mrt_close(self):
		self.soc.close()


	#### retransmit_checker ####
	def retransmit_checker(self):

		while len(self.to_send_buffer) > 0 or len(self.sent_no_ack_tbl) > 0:
			time.sleep(1)
			# Waits to check if any packets havnt got their acks
			# Copying the dict just incase items are added during the loop 
			loopable_dict = self.sent_no_ack_tbl.copy()

			for key, (packet, sent_time) in loopable_dict.items():
				# Package has timed out so we put it back in the to_send buffer 
				# and remove from no_ack buffer
				if key != -1 and sent_time + self.TIMEOUT < time.time():
					self.to_send_buffer.appendleft(packet)
					try:
						del self.sent_no_ack_tbl[key]
					except:
						pass

			del loopable_dict

		print("All ACKs recieved")

		# Send Fin_data_packet packet
		fin_data_packet = build_header(self.src_port, self.dst_port, fin=255)
		self.soc.sendall(fin_data_packet)
		self.sent_final_ack = True

		return


	#### client_recv_data ####
	def client_recv_data(self):

		while len(self.to_send_buffer) > 0 or len(self.sent_no_ack_tbl) > 0:
			try:
				self.soc.settimeout(0.5)
				p_ack, address = self.soc.recvfrom(1024)
				header = parse_header(bytearray(p_ack))
			except:
				continue

			try:
				del self.sent_no_ack_tbl[byte_to_int(header['ack_from'])]
			except:
				continue

			# Calculating sliding window size
			if is_congested(header):
				self.WINDOW_SIZE = 1
			else:
				if self.WINDOW_SIZE < 1024: self.WINDOW_SIZE = self.WINDOW_SIZE * 2

		return


	#### client_send_data ####
	def client_send_data(self):
		print(f"Sending {len(self.to_send_buffer)} packets")
		
		while len(self.to_send_buffer) > 0 or len(self.sent_no_ack_tbl) > 0:
			# send new packets if we recieved acks for prev packets
			no_ack_size = len(self.sent_no_ack_tbl)
			if no_ack_size < self.WINDOW_SIZE:

				# Sending packets until we reach window size 
				for i in range(self.WINDOW_SIZE - no_ack_size):
					try:
						if len(self.to_send_buffer) != 0:
							# Saving place in sent_no_ack_tbl for item about to be popped
							self.sent_no_ack_tbl[-1] = (None, None)
							# Getting next packet
							packet = self.to_send_buffer.pop()
							
							# Putting packet in sent dict
							seq_num = byte_to_int( parse_header(packet)["seq_num"] )
							self.sent_no_ack_tbl[seq_num] = (packet, time.time())

							#Sending packet after putting it in sent_no_ack_tbl
							self.soc.sendall(packet)
							
							del self.sent_no_ack_tbl[-1]

					except:
						print("Did not send")

		# print("client_send_data stopping")
		return

	def mrt_send(self, data):
		self.sent_final_ack = False
		# initilizing the packets and the buffers 
		self.to_send_buffer = packeterize_data(data, self.src_port, self.dst_port)
		self.sent_no_ack_tbl = {}
		self.total_acks = 0

		# Thread for recieving acks from server
		rec = Thread(target=self.client_recv_data).start()

		# Thread for sending data packets
		snd = Thread(target=self.client_send_data).start()

		# Thread for checking if packets need to be retransmitted
		ret = Thread(target=self.retransmit_checker).start()

		while True:
			if len(self.to_send_buffer) == 0 and len(self.sent_no_ack_tbl) == 0 and self.sent_final_ack:
				return



if __name__ == "__main__":
	fp = open("./romeo&julliet.txt", "r")
	str_data = fp.read()
	data = str_data.encode("utf-8")
	fp.close()

	client = MRT_client()
	client.mrt_connect(SERVER, S_PORT)
	client.mrt_send(data)
	client.mrt_disconnect()
	client.mrt_close()






