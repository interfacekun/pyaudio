import pyaudio
import wave
import numpy as np
import time
import os
import subprocess
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

def save_wave_file(filename, data):
	wf = wave.open(filename, 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes("".join(data))
	wf.close()

while True:
	string_audio_data = stream.read(CHUNK)
	audio_data = np.fromstring(string_audio_data, dtype=np.short)
	large_sample_count = np.sum(audio_data > LEVEL)
	temp = np.max(audio_data)
	if temp < 2000:
		print "temp < 2000 " + str(temp)
	if temp > 2000 and t == 0:
		t = 1 
		print 'signl begin record'
		begin = time.time()
		print "temp > 2000 " + str(temp)
		save_buffer.append(string_audio_data)
		stop_signal = 0
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			data_number = np.fromstring(data, dtype=np.short)
			save_buffer.append(data)
			temp = np.max(data_number)
			print "record temp: " + str(temp)
			if temp < 700:
				stop_signal += 1
				if stop_signal < 10:
					continue
				else:
					stop_signal = 0
					break
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
			print(time.time())
			cmd = 'python /root/pyaudio/recognise.py'
			os.system(cmd)
			#subprocess.call(["python","/root/pyaudio/recognise.py"])
			print("end recognise")
			print(time.time())
			p = pyaudio.PyAudio()
			stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)
			save_buffer = []
		time.sleep(0.01)

