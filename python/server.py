#!/usr/bin/python3
import csv
import socket
import telepot
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DayLocator, HourLocator, DateFormatter
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

LOG_MAX_LEN = 500
LOG_T_DELTA = datetime.timedelta(minutes=5)



def ToiletRecord(x):
	with open('data/toilet1_log.txt', 'r') as f:
		t_list = f.read().split(',')
	f.close()

	if len(t_list) > LOG_MAX_LEN:
		with open('data/toilet1_log.txt', 'w') as f:
			for i in t_list[-LOG_MAX_LEN+1:]:
				f.write(i+',')
			f.write(str(x))
	elif t_list == ['']:
		with open('data/toilet1_log.txt', 'a') as f:
			f.write(str(x))
	else:
		with open('data/toilet1_log.txt', 'a') as f:
			f.write(','+str(x))
	f.close()



def ToiletPlot():
	with open('data/toilet1_log.txt', 'r') as f:
		t_list = f.read().split(',')
	f.close()
	t_list = [float(i) for i in t_list]

	plt.hist(t_list, normed=False, bins=100) # bins: divide into 100 ranges
	
	plt.title('Average pooping time')
	plt.ylabel('frequency')
	plt.xlabel('time (sec)')
	plt.savefig('data/toilet1_plot.png')



def ToiletAvg(floor):
	if floor == 1:
		with open('data/toilet1_log.txt', 'r') as f:
			t_list = f.read().split(',')
		f.close()
		t_list = [float(i) for i in t_list]

		return sum(t_list)/len(t_list)
	elif floor == 2:
		return 102.7
	else:
		return 111.4



def CubicleRecord(worker, x):
	with open('data/cubicle'+str(worker)+'_log.txt', 'r') as f:
		t_list = f.read().split(',')
	f.close()

	if len(t_list) > LOG_MAX_LEN:
		with open('data/cubicle'+str(worker)+'_log.txt', 'w') as f:
			for i in t_list[-LOG_MAX_LEN+1:]:
				f.write(i+',')
			f.write(str(x))
	elif t_list == ['']:
		with open('data/cubicle'+str(worker)+'_log.txt', 'a') as f:
			f.write(str(x))
	else:
		with open('data/cubicle'+str(worker)+'_log.txt', 'a') as f:
			f.write(','+str(x))
	f.close()



def CubiclePlot(worker):
	with open('data/cubicle'+str(worker)+'_log.txt', 'r') as f:
		t_list = f.read().split(',')
	f.close()
	t_list = [float(i) for i in t_list]

	plt.hist(t_list, normed=False, bins=100) # bins: divide into 100 ranges
	
	plt.title('Average pooping time for worker '+str(worker))
	plt.ylabel('frequency')
	plt.xlabel('time (sec)')
	plt.savefig('data/cubicle'+str(worker)+'_plot.png')



def CubicleHourRecord(worker, isPresent):
	with open('data/cubicle'+str(worker)+'_hour_log.txt', 'r') as f:
		lines = f.readlines()
	f.close()

	this_hour = [int(i) for i in lines[datetime.datetime.now().hour].split(',')]
	if isPresent:
		this_hour[0] += 1
	else:
		this_hour[1] += 1

	lines[datetime.datetime.now().hour] = str(this_hour[0])+','+str(this_hour[1])+'\n'

	with open('data/cubicle'+str(worker)+'_hour_log.txt', 'w') as f:
		f.writelines(lines)
	f.close()



def CubicleHourPlot(worker):
	with open('data/cubicle'+str(worker)+'_hour_log.txt', 'r') as f:
		lines = f.readlines()
	f.close()

	ratio_list = []
	for line in lines:
		this_hour = [int(i) for i in line.split(',')]
		if this_hour[0] + this_hour[1] == 0:
			ratio_list.append(0)
		else:
			ratio_list.append(this_hour[0] / (this_hour[0] + this_hour[1]) * 100)

	plt.bar(np.arange(0,24), ratio_list, align='center')

	plt.xlim([-0.5,23.5])
	plt.title('Working time of worker '+str(worker))
	plt.ylabel('percentage')
	plt.xlabel('time (hour)')
	plt.savefig('data/cubicle'+str(worker)+'_hour_plot.png')



def BatteryRecord(x):
	now_t = datetime.datetime.now()

	with open ("battery_log.txt", "r") as f:
		lines = f.readlines()
	f.close()

	if len(lines) > 0:
		last_log = lines[-1].split(',')
		last_t = datetime.datetime.strptime(last_log[0], '%Y-%m-%d %I:%M:%S.%f')
	else:
		last_t = now_t

	# remove lines if necessiary
	if len(lines) > LOG_MAX_LEN:
		if now_t - last_t < LOG_T_DELTA:
			with open ("battery_log.txt", "w") as f:
				f.writelines(lines[-LOG_MAX_LEN:-1])
			f.close()
		else:
			with open ("battery_log.txt", "w") as f:
				f.writelines(lines[-LOG_MAX_LEN:])
			f.close()
	else:
		if now_t - last_t  < LOG_T_DELTA:
			with open ("battery_log.txt", "w") as f:
				f.writelines(lines[:-1])
			f.close()

	# write
	with open ("battery_log.txt", "a") as f:
		f.write(str(now_t)+','+str(x)+'\n')
	f.close()



def BatteryPlot():

	with open ("battery_log.txt", "r") as f:
		r = csv.reader(f)
		t_list = []
		value_list = []
		for row in r:
			t_list.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %I:%M:%S.%f'))
			value_list.append(row[1])
	f.close()

	t_list = date2num(t_list)

	fig, ax = plt.subplots()
	ax.plot_date(t_list, value_list, 'b-')
	ax.xaxis.set_major_locator(DayLocator())
	ax.xaxis.set_minor_locator(HourLocator(np.arange(0, 25, 6)))
	ax.xaxis.set_major_formatter(DateFormatter('\n%m-%d'))
	ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))

	ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
	fig.autofmt_xdate()


	plt.title('Battery level')
	plt.ylabel('fuel level')
	plt.xlabel('time')
	plt.savefig('data/battery_plot.png')



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

			if words[0] == 'B':
				BatteryRecord(words[1])

			else:
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

				if toilet_id ==  '1':
					toilet1_state == stall_state
				for i in wait_t:
					ToiletRecord(i)


toilet1_state = []
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
						with open('data/toilet1_plot.png', 'rb') as f:
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
			if len(toilet1_state) == 0:
				bot.sendMessage(from_id, '*1/F*\nNo data yet', parse_mode='Markdown')
			else:
				reply_str = '*1/F*\n'

				all_occupied = True
				# check state
				i = 1
				for state in toilet1_state:
					reply_str += str(i) + ': '
					if state == True:
						reply_str += 'Occupied\n'
					else:
						reply_str += 'Vacant\n'
						all_occupied = False
					i += 1

				bot.sendMessage(from_id, reply_str, parse_mode='Markdown')
				if all_occupied:
					bot.sendMessage(from_id, 'No stall is vacant\nAverage Waiting Time: '+str(ToiletAvg(1)))
					bot.sendMessage(from_id, 'You may go to the toilet on 2/F\nVacant stalls: 1, 4, 5')
		elif commands[1] == '2':
			bot.sendMessage(from_id, '*2/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Vacant\n5: Vacant\n', parse_mode='Markdown')
		elif commands[1] == '3':
			bot.sendMessage(from_id, '*3/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Occupied\n', parse_mode='Markdown')



if __name__ == '__main__':
	bot = telepot.Bot('568594704:AAEeL4ThpMiwRg2B6lCbKdiRRl0HYaWn-e0')

	MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
	
	# Keep the program running.
	print ('Listening ...')
	TCPListener()
