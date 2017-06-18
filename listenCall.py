#-*- coding:utf-8 -*-
import pyaudio
import wave
import numpy as np
import time
import os
import subprocess
import redis
import thread
con = redis.Redis(host='127.0.0.1', port=6379, db=0, password='627795061')
p = pyaudio.PyAudio()
print(p.get_default_input_device_info())
print(p.get_default_output_device_info())
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
LEVEL = 1500
COUNT_NUM = 20
RATE = 16000
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "/root/pyaudio/audio/output.wav"
SAVE_LENGTH = 8


stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

print("* recording")
save_count = 0
save_buffer = []
t = 0
sum = 0
time_flag = 0
flag_num = 0
filename = ''
duihua = '1'
begin = 0

threshold = 2000
thresholdKey = "config:threshold"

def save_wave_file(filename, data):
	wf = wave.open(filename, 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes("".join(data))
	wf.close()
def startShowText():
	cmd = 'python /root/pyaudio/showMsg.py 4m等待语音输入'
	#print chardet.detect(cmd)
	os.system(cmd)
thread.start_new_thread(startShowText,())
def playDing():
	#cmd = 'mplayer /root/pyaudio/audio/ding.mp3'
	#os.system(cmd)
	cmd = 'python /root/pyaudio/recognise.py'
	os.system(cmd)
	

while True:
	try:
		string_audio_data = stream.read(CHUNK)
	except Exception as e:
		print e
		continue
	audio_data = np.fromstring(string_audio_data, dtype=np.short)
	large_sample_count = np.sum(audio_data > LEVEL)
	temp = np.max(audio_data)
	#if temp < 2000:
		# print "temp < 2000 " + str(temp)
	threshold = int(con.get(thresholdKey))
	if temp > threshold and t == 0:
		t = 1 
		print 'signl begin record'
		begin = time.time()
		print ("temp > %d %d") % (threshold, temp)
		save_buffer.append(string_audio_data)
		stop_signal = 0
		startSignal = 1
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			data_number = np.fromstring(data, dtype=np.short)
			save_buffer.append(data)
			temp = np.max(data_number)
			print("i %d")%(i)
			if temp > threshold:
				startSignal += 1
			if i >= 3 and startSignal < 3:
				print("startSignal %d")%(startSignal)
				save_buffer=[]
				break
			print "record temp: " + str(temp)
			if temp < 700:
				stop_signal += 1
				if stop_signal < 5:
					continue
				else:
					stop_signal = 0
					break
		print("save_buffer len %d") % (len(save_buffer))
		if len(save_buffer) > 0:
			filename = WAVE_OUTPUT_FILENAME
			flag_num += 1

			save_wave_file(filename, save_buffer)
			save_buffer = []
			t = 0
			sum =0
			time_flag = 0
			print filename, 'save'
			print("* done recording")
			print("bigin recognise")
			thread.start_new_thread(playDing,())
			cmd = 'play -q /root/pyaudio/audio/ding.wav'
			os.system(cmd)
			#subprocess.call(["python","/root/pyaudio/recognise.py"])
			print("end recognise")

			p = pyaudio.PyAudio()
			stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)
		save_buffer = []
		t = 0
		sum =0
		time_flag = 0
		time.sleep(0.01)

