#!/usr/bin/python3
import socket

if __name__ == '__main__':

	TCP_IP = '192.168.0.191'
	TCP_PORT = 38763
	BUFFER_SIZE = 1024
	'''
	TOILET_ID = 2
	STALL_NUM = 5
	stall_state = ['0'] * STALL_NUM
	wait_t_buffer = [15, 25]
	MSG_HEADER = str(TOILET_ID) + ' ' + str(STALL_NUM)
	'''
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	'''
	msg = MSG_HEADER

	for i in stall_state:
		msg += ' ' + i

	while len(wait_t_buffer) > 0:
		msg += ' ' + str(wait_t_buffer.pop())
	'''

	msg = '1 2 1 0 10\nC 1 0 0 0 15 0 0 0\nB 3.14\n'

	s.send(msg.encode('utf-8'))
	#data = s.recv(BUFFER_SIZE)
	s.close()

	#print ("received data:", data)
