#! /usr/bin/env python
#-*- coding:utf-8 -*-
import base64
import json
import urllib2
import sys
import os
import fcntl
import thread
import commands
import time
import redis
import chardet
import datetime
import binascii

reload(sys)
sys.setdefaultencoding('utf8')
# cmar='arecord -r 16000 -d 2 -D plughw:1 -f S16 /root/mypython/nihao.wav'
# os.system(cmar)

def startShowText():
	cmd = 'python /root/pyaudio/showMsg.py 4m等待识别'
	#print chardet.detect(cmd)
	os.system(cmd)

thread.start_new_thread(startShowText,())

def baidu_asr(speech_file, json_data, access_token, mac_address):
	with open(speech_file, 'rb') as f:
		speech_data = f.read()
	speech_base64=base64.b64encode(speech_data).decode('utf-8')
	speech_length=len(speech_data)
	data_dict = {'format':'wav', 'rate':16000, 'channel':1, 'cuid':mac_address, 'token':access_token, 'lan':'zh', 'speech':speech_base64, 'len':speech_length}
	json_data = json.dumps(data_dict).encode('utf-8')
	json_length = len(json_data)
	request = urllib2.Request(url='http://vop.baidu.com/server_api')
	request.add_header("Content-Type", "application/json")
	request.add_header("Content-Length", json_length)
	fs = urllib2.urlopen(url=request, data=json_data)
	result_str = fs.read().decode('utf-8')
	json_resp = json.loads(result_str)
	return json_resp

def showSay(say, say_file):
	# f=open(say_file,'w')
	# fcntl.flock(f, fcntl.LOCK_EX)
	# f.write(say)
	# fcntl.flock(f, fcntl.LOCK_UN)
	cmd = 'python /root/pyaudio/showMsg.py 2m'+say
	os.system(cmd)	

apiKey = "dlSwkVT56CHwmnZHA4fy3UGj"
secretKey = "01a19cd0b0fd35c16f83c4d9107d4a5e"
auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;
mac_address = "b8:27:eb:cb:99:f3"
wav_file = "/root/pyaudio/audio/output.wav"
say_file = "/root/gpio/say.txt"
say = ""

con = redis.Redis(host='127.0.0.1', port=6379, db=0, password='627795061')

modelKey = "config:model"
# startTime = datetime.datetime.now().microsecond
#print "startTime", startTime
testTime1 = time.time()
if con.get(modelKey) == "online":
	try:
		res = urllib2.urlopen(auth_url)
		json_data = res.read().decode("utf-8")  
		access_token = json.loads(json_data)['access_token']
		
		json_resp = baidu_asr(wav_file, json_data, access_token, mac_address)
		str=json.dumps(json_resp['result'], ensure_ascii=False)
		say=str[2:-3]
		thread.start_new_thread(showSay,(say, say_file))
		print say
	except Exception as e:
		print("dfdddsafasdf1")
		print "eeeee", e
		cm = "python /root/pyaudio/offlineVoice.py"
		(status, say) = commands.getstatusoutput(cm)
		say = say[0:-3]
		if len(say) > 0:
			thread.start_new_thread(showSay,(say, say_file))
		print "esay", say, len(say)
else:
	print("dfdddsafasdf2")
	cm = "python /root/pyaudio/offlineVoice.py"
	(status, say) = commands.getstatusoutput(cm)
	thread.start_new_thread(showSay,(say, say_file))
	say = say[0:-3]

# cm = "python /root/pyaudio/offlineVoice.py"
# (status, say) = commands.getstatusoutput(cm)
# say=say[0:-3]
# print say
# thread.start_new_thread(showSay,(say, say_file))

#cm='nohup python /root/pyaudio/robot.py '+say+' > /dev/null 2>&1'
# stopTime = datetime.datetime.now().microsecond
# print "stopTime", stopTime
# useTime = stopTime - startTime
# print "reconise use time:", useTime
# say2 = say.encode('utf-8')
# print chardet.detect(say2)
# say2 = binascii.b2a_hex(say2)
# print say2
testTime2 = time.time()
totalTime = testTime2 - testTime1
print("recognise use time:%f") % totalTime

if len(say) == 0:
	cmd = 'python /root/pyaudio/showMsg.py 4m等待语音输入'
	#print chardet.detect(cmd)
	os.system(cmd)
else:
	cm='python /root/pyaudio/robot.py '+say
	os.system(cm)
