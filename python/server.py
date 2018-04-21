#!/usr/bin/python3
import socket
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

def TCPListener():

	TCP_PORT = 38763
	BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

	toilet_state = {}



	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', TCP_PORT))
	s.listen(1)

	while True:
		conn, addr = s.accept()
		print ('Connection address:', addr)

		data_string = b''
		while True:
			data = conn.recv(BUFFER_SIZE)
			if not data: break
			data_string += data
			#data = bytearray()
			#conn.send(data)  # echo
		conn.close()
		print ("received data:", data_string)

		if len(data_string) > 0:
			words = data_string.decode('utf-8').split(' ')

			toilet_id = words[0]
			stall_num = int(words[1])
			stall_state = []
			for word in words[2:2+stall_num]:
				stall_state.append(word == '0')
			wait_t = []
			for word in words[2+stall_num:]:
				wait_t.append(int(word))

			print(toilet_id)
			print(stall_state)
			print(wait_t)



manager_set = set()
PASSWORD = 'elpsycongroo'

def on_chat_message(msg):
	global manager_set

	menu_vacancy = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='1/F', callback_data='toilet 1')],
		[InlineKeyboardButton(text='2/F', callback_data='toilet 2')],
		[InlineKeyboardButton(text='3/F', callback_data='toilet 3')],
	])

	content_type, chat_type, chat_id = telepot.glance(msg)
	from_id = msg['from']['id']

	if content_type == 'text':
		commands = msg['text'].strip().lower().split(' ')

		if commands[0] == '/su':
			if len(commands) > 1:
				if commands[1] == PASSWORD:
					manager_set.add(from_id)
					bot.sendMessage(from_id, 'Manager Mode Activated')
				else:
					bot.sendMessage(from_id, 'Wrong Manager Password')
			else:
					bot.sendMessage(from_id, 'Usage: /su <password>')

		elif commands[0] == '/stat':
			if from_id in manager_set:
				if len(commands) > 1:
					if commands[1] == '1':
						with open('hist1.png', 'rb') as f:
							bot.sendPhoto(from_id, f)
				else:
					bot.sendMessage(from_id, 'Usage: /stat <floor>')
			else:
				bot.sendMessage(from_id, 'Error: Not in Manager Mode')

		else:
			bot.sendMessage(from_id, 'Which floor?', reply_markup = menu_vacancy)



def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	commands = query_data.split(' ')

	if commands[0] == 'toilet':
		if commands[1] == '1':
			bot.sendMessage(from_id, '*1/F*\n1: Occupied\n2: Occupied', parse_mode='Markdown')
			bot.sendMessage(from_id, 'No stall is vacant\nYou may go to the toilet on 2/F\nVacant stalls: 1, 4, 5')
		elif commands[1] == '2':
			bot.sendMessage(from_id, '*2/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Vacant\n5: Vacant', parse_mode='Markdown')
		elif commands[1] == '3':
			bot.sendMessage(from_id, '*3/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Occupied', parse_mode='Markdown')



if __name__ == '__main__':
	bot = telepot.Bot('568594704:AAEeL4ThpMiwRg2B6lCbKdiRRl0HYaWn-e0')

	MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
	
	# Keep the program running.
	print ('Listening ...')
	TCPListener()
