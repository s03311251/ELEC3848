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
employee_name = ['Alice', 'Bob', 'Charles', 'Dave']



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
	plt.clf()



def ToiletAvg(floor):
	if floor == 1:
		with open('data/toilet1_log.txt', 'r') as f:
			t_list = f.read().split(',')
		f.close()
		if len(t_list) > 0:
			t_list = [float(i) for i in t_list]
			return sum(t_list)/len(t_list)
		else:
			return 65535
			
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
	
	if len(t_list) <= 1:
		return False
	
	t_list = [float(i) for i in t_list]

	plt.hist(t_list, normed=False, bins=100) # bins: divide into 100 ranges

	plt.title('Average pooping time for '+employee_name[worker-1])
	plt.ylabel('frequency')
	plt.xlabel('time (sec)')
	plt.savefig('data/cubicle'+str(worker)+'_plot.png')
	plt.clf()
	
	return True



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
	plt.title('Working time of worker '+employee_name[worker-1])
	plt.ylabel('percentage')
	plt.xlabel('time (hour)')
	plt.savefig('data/cubicle'+str(worker)+'_hour_plot.png')
	plt.clf()


def BatteryRecord(x):
	now_t = datetime.datetime.now()

	with open ("data/battery_log.txt", "r") as f:
		lines = f.readlines()
	f.close()

	if len(lines) > 0:
		last_log = lines[-1].split(',')
		last_t = datetime.datetime.strptime(last_log[0], '%Y-%m-%d %H:%M:%S.%f')
	else:
		last_t = now_t
	'''	
	# remove lines if necessiary
	if len(lines) > LOG_MAX_LEN:
		if now_t - last_t < LOG_T_DELTA:
			with open ("data/battery_log.txt", "w") as f:
				f.writelines(lines[-LOG_MAX_LEN:-1])
			f.close()
		else:
			with open ("data/battery_log.txt", "w") as f:
				f.writelines(lines[-LOG_MAX_LEN:])
			f.close()
	else:
		if now_t - last_t  < LOG_T_DELTA:
			with open ("data/battery_log.txt", "w") as f:
				f.writelines(lines[:-1])
			f.close()
	'''
	if (now_t - last_t)  > LOG_T_DELTA:
		# write
		with open ("data/battery_log.txt", "a") as f:
			f.write(str(now_t)+','+str(x))
		f.close()
	
	
	
def BatteryCurrLevel():
	with open ("data/battery_log.txt", "r") as f:
		lines = f.readlines()
	f.close()

	if len(lines) > 0:
		last_log = lines[-1].split(',')
		return True, float(last_log[1])
		
	return False, 0
	

def BatteryPlot():

	with open ("data/battery_log.txt", "r") as f:
		r = csv.reader(f)
		t_list = []
		value_list = []
		for row in r:
			t_list.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
			value_list.append(float(row[1]))
	f.close()

	if len(t_list) <= 1:
		return False
	
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
	plt.clf()

	return True
	


def TCPListener():
	global toilet1_state, cubicle_state

	TCP_PORT = 38763
	BUFFER_SIZE = 1024  # Normally 1024, but we want fast response



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

		command_list = data_string.decode('utf-8').split('\n')
		for command in command_list:
			if len(command) > 0:
				print (command)
				words = command.split(' ')

				if words[0] == 'B':
					if len(words) >= 2:
						BatteryRecord(words[1])
					else:
						print ('Error: B msg not complete')


				elif words[0] == 'C':
					if len(words) >= 9:
						cubicle_state = [i == '1' for i in words[1:5]]
						cubicle_t = [int(i) for i in words[5:9]]
						for i in [1,2,3,4]:
							CubicleHourRecord(i, cubicle_state[i-1])
							if cubicle_t[i-1] != 0:
								CubicleRecord(i, cubicle_t[i-1])
					else:
						print ('Error: C msg not complete')

				else:
					toilet_id = words[0]
					stall_num = int(words[1])
					stall_state = []
					for word in words[2:2+stall_num]:
						print (word)
						stall_state.append(int(word) == 1)
					wait_t = []
					if len(words) > 2+stall_num: # somebody has left the stall
						for word in words[2+stall_num:]:
							wait_t.append(int(word))

					print(toilet_id)
					print(stall_state)
					print(wait_t)

				if toilet_id == '1':
					toilet1_state = stall_state
					for i in wait_t:
						ToiletRecord(i)


toilet1_state = []
cubicle_state = []
manager_set = set()
PASSWORD = 'elpsycongroo'



def on_chat_message(msg):
	global manager_set

	menu_toilet = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='1/F', callback_data='toilet 1')],
		[InlineKeyboardButton(text='2/F', callback_data='toilet 2')],
		[InlineKeyboardButton(text='3/F', callback_data='toilet 3')],
	])

	menu_su = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Toilet Vacancy', callback_data='su toilet')],
		[InlineKeyboardButton(text='Toilet Stat', callback_data='su toilet_stat')],
		[InlineKeyboardButton(text='Cubicle Condition', callback_data='su cubicle')],
		[InlineKeyboardButton(text='Cubicle Stat', callback_data='su cubicle_stat')],
		[InlineKeyboardButton(text='Battery Stat', callback_data='su battery')],
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
					bot.sendMessage(from_id, 'Manager Menu:', reply_markup = menu_su)
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
						f.close()
					elif commands[1] == 'c':
						if len(cubicle_state) == 0:
							bot.sendMessage(from_id, '*Cubicle*\nNo data yet', parse_mode='Markdown')
						else:
							reply_str = '*Cubicle*\n'

							# check state
							i = 0
							for state in cubicle_state:
								reply_str += employee_name[i] + ': '
								if state == True:
									reply_str += 'Present\n'
								else:
									reply_str += 'Absent\n'
								i += 1

							bot.sendMessage(from_id, reply_str, parse_mode='Markdown')
				else:
					bot.sendMessage(from_id, 'Usage: /stat <floor>')
			else:
				bot.sendMessage(from_id, 'Error: Not in Manager Mode')

		elif from_id in manager_set:
			bot.sendMessage(from_id, 'Manager Menu:', reply_markup = menu_su)
		else:
			bot.sendMessage(from_id, 'Which floor?', reply_markup = menu_toilet)



def on_callback_query(msg):

	menu_toilet = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='1/F', callback_data='toilet 1')],
		[InlineKeyboardButton(text='2/F', callback_data='toilet 2')],
		[InlineKeyboardButton(text='3/F', callback_data='toilet 3')],
	])

	menu_toilet_stat = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='1/F', callback_data='toilet_stat 1')],
		[InlineKeyboardButton(text='2/F', callback_data='toilet_stat 2')],
		[InlineKeyboardButton(text='3/F', callback_data='toilet_stat 3')],
	])

	menu_cubicle_stat = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Alice', callback_data='cubicle_stat 1')],
		[InlineKeyboardButton(text='Bob', callback_data='cubicle_stat 2')],
		[InlineKeyboardButton(text='Charles', callback_data='cubicle_stat 3')],
		[InlineKeyboardButton(text='Dave', callback_data='cubicle_stat 4')],
	])



	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	commands = query_data.split(' ')

	# Toilet Menu
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
					bot.sendMessage(from_id, 'No stall is vacant\nAverage Waiting Time: '+str(round(ToiletAvg(1), 2))+' seconds')
					bot.sendMessage(from_id, 'You may go to the toilet on 2/F\nnumber of vacant stalls: 2')

		elif commands[1] == '2':
			bot.sendMessage(from_id, '*2/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Vacant\n5: Occupied\n', parse_mode='Markdown')

		elif commands[1] == '3':
			bot.sendMessage(from_id, '*3/F*\n1: Vacant\n2: Occupied\n3: Occupied\n4: Occupied\n', parse_mode='Markdown')



	# Manager Menu
	elif from_id not in manager_set:
				bot.sendMessage(from_id, 'Error: Not in Manager Mode')

	elif commands[0] == 'su':
		if commands[1] == 'toilet':
			bot.sendMessage(from_id, 'Which floor?', reply_markup = menu_toilet)

		elif commands[1] == 'toilet_stat':
			bot.sendMessage(from_id, 'Which floor?', reply_markup = menu_toilet_stat)

		elif commands[1] == 'cubicle':
			if len(cubicle_state) == 0:
				bot.sendMessage(from_id, '*Cubicle*\nNo data yet', parse_mode='Markdown')
			else:
				reply_str = '*Cubicle*\n'
				# check state
				i = 0
				for state in cubicle_state:
					reply_str += employee_name[i] + ': '
					if state == True:
						reply_str += 'Present\n'
					else:
						reply_str += 'Absent\n'
					i += 1
				bot.sendMessage(from_id, reply_str, parse_mode='Markdown')

		elif commands[1] == 'cubicle_stat':
			bot.sendMessage(from_id, 'Which Employee?', reply_markup = menu_cubicle_stat)

		elif commands[1] == 'battery':
			hasData, level = BatteryCurrLevel()
			if hasData:
				bot.sendMessage(from_id, 'Fuel Level: '+str(round(level, 2))+' V')
				
				bot.sendMessage(from_id, 'Drawing Plot')
				if BatteryPlot():
					bot.sendMessage(from_id, 'Sending Plot')
					with open('data/battery_plot.png', 'rb') as f:
						bot.sendPhoto(from_id, f)
					f.close()
				else:
					bot.sendMessage(from_id, 'Error: Insufficient Data')

			else:
				bot.sendMessage(from_id, 'Error: Open battery log failed')
				



	elif commands[0] == 'toilet_stat':
		bot.sendMessage(from_id, 'Drawing Plot')
		if commands[1] == '1':
			ToiletPlot()

		bot.sendMessage(from_id, 'Sending Plot')
		with open('data/toilet'+commands[1]+'_plot.png', 'rb') as f:
			bot.sendPhoto(from_id, f)
		f.close()



	elif commands[0] == 'cubicle_stat':

		bot.sendMessage(from_id, 'Drawing Plot')
		CubicleHourPlot(int(commands[1]))
		if CubiclePlot(int(commands[1])):
			bot.sendMessage(from_id, 'Sending Plot')
			with open('data/cubicle'+commands[1]+'_plot.png', 'rb') as f:
				bot.sendPhoto(from_id, f)
			f.close()
			with open('data/cubicle'+commands[1]+'_hour_plot.png', 'rb') as f:
				bot.sendPhoto(from_id, f)
			f.close()
		else:
			bot.sendMessage(from_id, 'Error: No data.\nGenius! This guy don\'t need to go to toilet!')








if __name__ == '__main__':
	bot = telepot.Bot('568594704:AAEeL4ThpMiwRg2B6lCbKdiRRl0HYaWn-e0')

	MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
	
	# Keep the program running.
	print ('Listening ...')
	TCPListener()
