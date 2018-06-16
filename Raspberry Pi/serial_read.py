#!/usr/bin/env python
          
import struct     
import time
from datetime import datetime
import serial
import csv
import os

cur_path = '/home/pi/Desktop/MarkUp/data/'
      
ser = serial.Serial(
              
	port='/dev/serial0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=5
	)

start = datetime.now()
t_end = time.time() + 60*60*6
print cur_path

          
header = ['Time','Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz']
fileid = cur_path + datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
print 'Started at', start
f = open(fileid + '.csv','a')
writer = csv.writer(f)
writer.writerow(header)
f.close()

state = 0
got_accel = 0
got_gyro = 0
meas_time = 0
meas_timeout_flag = 0

while time.time() < t_end:
	x = ser.read(1)
	print state

	if state == 0:
        	if x == b'a':
			state = 1
		if x == b'g':
			state = 11
		else:
			pass

	elif state == 11:
		if x == b'g':
			state = 12
		else:
			state = 0
	elif state == 1:
        	if x == b'a':
			state = 2
        	else:
			state = 0
	elif state == 2:
        	adata = ser.read(11)
        	adata = x + adata
		accel_data = struct.unpack('<fff', adata)
        	state = 0
		got_accel = 1

		print accel_data

	elif state == 12:
        	gdata = ser.read(11)
        	gdata = x + gdata
		gyro_data = struct.unpack('<fff', gdata)
        	state = 0
		got_gyro = 1

        	print gyro_data

	if got_accel+got_gyro == 2:

		localtime = datetime.now().strftime('%H:%M:%S:%f')[:-3]
		f = open(fileid + '.csv','a')
		writer = csv.writer(f)
		writer.writerow([localtime, accel_data[0], accel_data[1], accel_data[2], gyro_data[0], gyro_data[1], gyro_data[2]])
		f.close()

		meas_time = time.time()
		meas_timeout_flag = 1

		got_accel = 0
		got_gyro = 0

	if time.time() - meas_time > 1:

		if meas_timeout_flag == 1:

			meas_timeout_flag = 0

			fileid = cur_path + datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
			print 'Started again at', start
			f = open(fileid + '.csv','a')
			writer = csv.writer(f)
			writer.writerow(header)
			f.close()

	# if x != b"a":
		# print 'hello'
