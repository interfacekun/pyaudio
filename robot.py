#! /usr/bin/env python
#-*- coding:utf-8 -*-
import json
import urllib
import urllib2
import sys
import random
import os
import fcntl
import thread
import redis
import re
import time

reload(sys)  
sys.setdefaultencoding('utf8')

def startShowText():
	cmd = 'python /root/pyaudio/showMsg.py 4m等待回复'
	os.system(cmd)
# thread.start_new_thread(startShowText,())

def baidu_asr():
	#userID=random.randint(1, 100)
	userID="b827ebcb99f3"
	#mykey="ecb4976819bb565ac65916070cd425f8"
	mykey="2ba52d0c1f3341d18be2e48fc4405b3d"
	msg=sys.argv[1]
	#jdata = {"key":"ecb4976819bb565ac65916070cd425f8","info":msg}
	#json_data = json.dumps(jdata).decode('utf-8')
	#request = urllib2.Request('http://www.tuling123.com/openapi/api',json_data)
	url='http://www.tuling123.com/openapi/api'
	
	#request.get_method = lambda:'POST'
	#url='http://www.tuling123.com/openapi/api?key='+mykey+'&info='+msg+'&userid='+str(userID)
	#request.add_header('Content-Type', 'application/json')
	json_data = urllib.urlencode({"key":mykey,"info":msg,"userid":str(userID)})
	fs=urllib2.urlopen(url=url, data=json_data)
	#fs = urllib2.urlopen(url)
	result_str = fs.read().decode('utf-8')
	json_resp = json.loads(result_str,encoding="utf-8")
	return json_resp

def showSay(say):
	# f=open('/root/gpio/say.txt','w')
	# fcntl.flock(f, fcntl.LOCK_EX)
	# f.write(say)
	# fcntl.flock(f, fcntl.LOCK_UN)
	cmd = 'python /root/pyaudio/showMsg.py '+say
	print cmd
	os.system(cmd)

def sendWxMsg(msg):
	cmd = 'python /root/itchat/wxClient.py ' + msg
	print cmd
	os.system(cmd)

say = ""
con = redis.Redis(host='127.0.0.1', port=6379, db=0, password='627795061')
apiKey="dlSwkVT56CHwmnZHA4fy3UGj"
secretKey="01a19cd0b0fd35c16f83c4d9107d4a5e"
auth_url="https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;
modelKey = "config:model"

if re.search(r'室内温度', sys.argv[1]):
		tfile = open("/sys/bus/w1/devices/28-0415a14811ff/w1_slave")
		fcntl.flock(tfile, fcntl.LOCK_EX)
		text = tfile.read()
		fcntl.flock(tfile,fcntl.LOCK_UN)
		tfile.close()
		secondline = text.split("\n")[1]
		temperaturedata = secondline.split(" ")[9]
		temperature = float(temperaturedata[2:])
		temperature = temperature / 1000
		temper = int(temperature) - 5
		rawSay = '室内温度为：' + str(temper) + '°'
		say = '2m'+rawSay
		showSay(say)

		if con.get(modelKey) == "online":
			try:
				res = urllib2.urlopen(auth_url)  
				json_data = res.read().decode("utf-8")  
				access_token = json.loads(json_data)['access_token']
				#cm='nohup /root/mypython/play.sh '+say+' '+access_token+' > /dev/null 2>&1'
				#cm='nohup /root/pyaudio/play.sh '+say+' '+access_token+' '+'1'+' > /dev/null 2>&1'

				cm='/root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'1'
				# print cm 
				os.system(cm)
			except Exception as e:
				print e

				cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'0'+' > /dev/null 2>&1'
				#cm='/root/pyaudio/play.sh '+say+' '+access_token+' '+'0'
				# print cm
				os.system(cm)
		else:

			cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'0'+' > /dev/null 2>&1'
			#cm='/root/pyaudio/play.sh '+say+' '+access_token+' '+'0'
			# print cm
			os.system(cm)
else:

	wx = re.match(r'给(.+?)发送消息(.+)', sys.argv[1])
	if wx:
		print wx.group(1), wx.group(2)
		say = '1m'+wx.group(2)+'m'+wx.group(1)
		sendWxMsg(say)
	else:
		thread.start_new_thread(startShowText,())
		regularList = con.keys("regular:*")
		reply_value = ""
		haveReply = False
		for i in regularList:
			pattern = i[8:]
			if re.search(pattern, sys.argv[1]):
				print i
				reply_key = con.get(i)
				reply_value = con.get(reply_key)
				print reply_value
				break

		if reply_value == "":
			reply_key = 'reply:' + sys.argv[1]
			reply_value = con.get(reply_key)
			print "test", reply_value

		if reply_value:
			haveReply = True
			rawSay = reply_value
			say = '2m' + reply_value
			cmd_key = 'cmd:' + reply_key[6:]
			print cmd_key
			cmd_value = con.get(cmd_key)
			print cmd_value
			if cmd_value:
				os.system(cmd_value)
		else:
			try:
				json_resp = baidu_asr()
				#print json.dumps(json_resp["text"],ensure_ascii=False)
				rawSay = json_resp["text"]
				rawSay = rawSay.replace(' ', '；')
				rawSay = rawSay.replace(';', '；')
				#rawSay = rawSay.replace('°', '度')
				rawSay = rawSay.replace(',', '，')
				rawSay = rawSay.replace(':', '：')
				#rawSay = rawSay.replace('-', '到')
				print "rawSay", rawSay
				say='2m' + rawSay
			except Exception as e:
				print e
				offline_key = "reply:onffline"
				offline_value = con.get(reply_key)
				rawSay = offline_value
				say = '2m' + rawSay
		showSay(say)

		# apiKey="dlSwkVT56CHwmnZHA4fy3UGj"
		# secretKey="01a19cd0b0fd35c16f83c4d9107d4a5e"
		# auth_url="https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;

		#modelKey = "config:model"
		if con.get(modelKey) == "online":
			try:
				res = urllib2.urlopen(auth_url)  
				json_data = res.read().decode("utf-8")  
				access_token = json.loads(json_data)['access_token']
				#cm='nohup /root/mypython/play.sh '+say+' '+access_token+' > /dev/null 2>&1'
				#cm='nohup /root/pyaudio/play.sh '+say+' '+access_token+' '+'1'+' > /dev/null 2>&1'
				if haveReply:
					cm='/root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'2 '+reply_key+'.mp3'
					os.system(cm)
				else:
					cm='/root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'1'
					# print cm 
					os.system(cm)
			except Exception as e:
				print e
				if haveReply:
					cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'2 '+reply_key+'.mp3'+' > /dev/null 2>&1'
					os.system(cm)
				else:
					cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'0'+' > /dev/null 2>&1'
					#cm='/root/pyaudio/play.sh '+say+' '+access_token+' '+'0'
					# print cm
					os.system(cm)
		else:
			if haveReply:
				cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'2 '+reply_key+'.mp3'+' > /dev/null 2>&1'
				os.system(cm)
			else:
				cm='nohup /root/pyaudio/play.sh '+rawSay+' '+access_token+' '+'0'+' > /dev/null 2>&1'
				#cm='/root/pyaudio/play.sh '+say+' '+access_token+' '+'0'
				# print cm
				os.system(cm)
#thread.start_new_thread(showSay,(say,))
#thread.start_new_thread(sendWxMsg,(say,))
	#showSay(say)
