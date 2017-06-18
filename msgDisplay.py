#!/usr/bin/env python
#-*- coding:utf-8 -*-
import socket
import os
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
import time
import Image
import ImageDraw
import ImageFont
import sys
import chardet
import struct 
import fcntl
import thread
import linecache

sock = None
conn = None
DC = None
RST = None
SPI_PORT = None
SPI_DEVICE = None
disp = None
font = None
image = None
draw = None
temper = None
sayT=u'语音识别未启动'
ip='网络未连接'
ip=ip.decode('utf-8')
ip_x=(LCD.LCDWIDTH-len(ip) * 10) / 2
lcdWidth=LCD.LCDWIDTH
data = None

def init():
	global sock
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	global conn
	conn = '/tmp/disMsg.txt'
	if not os.path.exists(conn):
		os.mknod(conn)
	if os.path.exists(conn):
		os.unlink(conn)
		sock.bind(conn)
		sock.listen(10)
	DC = 9
	RST = 3
	SPI_PORT = 0
	SPI_DEVICE = 0

	global disp
	disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
	global font
	font = ImageFont.truetype('/root/gpio/yahei.ttf', 10)
	disp.begin(contrast=60)
	disp.clear()
	disp.display()
	global image
	image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
	global draw
	draw = ImageDraw.Draw(image)

def showMsg(msg):
	print "showMsg:%s" %msg
	draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
	#print 123
	try:
		msg = msg.decode('utf-8')
	except Exception as e:
		print e
		draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
		draw.text((0, 3), "消息格式不正确".decode('utf-8'), font=font)
		return

	cutData = len(msg)/8
	if cutData == 0:
		cutData = 1
	print cutData
	
	if len(msg)%8 > 0 and len(msg) > 8:
		cutData = cutData + 1
	k = 0
	for i in range(0, cutData):
		#print(len(msg))
		#print chardet.detect(msg)
		try:
			tmp = msg[(8*i):(8*(i+1))]
			#print 'cut tmp', tmp

			#tmp = tmp.decode('utf-8')
		except Exception as e:
			print e
			draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
			draw.text((0, 3), "消息格式不正确".decode('utf-8'), font=font)
			break
		# tmp = msg
		# print tmp
		#print("456")
		print("tmp %d :%s")%(i, tmp)
		if k == 0:
			draw.text((0, 3),tmp,font=font)
		if k == 1:
			draw.text((0, 16),tmp,font=font)
		if k == 2:
			draw.text((0, 26),tmp,font=font)
		if k == 3:
			draw.text((0, 36),tmp,font=font)
			k = -1
		if i%4 == 3:
			disp.image(image)
			disp.display()
			time.sleep(8)
			draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
			print("sleep end")
		k = k + 1
	# image = Image.open('/root/itchat/NQR.png').convert('1')
	disp.image(image)
	disp.display()
	time.sleep(4)

def getip(ethname):   
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15]))[20:24])

def getIPThread():
	while True:
		try:
			global ip
			global ip_x
			ip=getip('wlan0')
			ip_x=(LCD.LCDWIDTH-len(ip) * 6) / 2
		except Exception,e:
			time.sleep(1)
			continue
		break
def getTemperature():
	global temper
	while True:
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
		time.sleep(60)

def showStatus():
	global data
	global draw
	global disp
	global lcdWidth
	global sayT
	global ip
	global temper
	while True:
		if data == None:
			draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
			ISOTIMEFORMAT='%Y-%m-%d'
			dateT=time.strftime(ISOTIMEFORMAT, time.localtime())
			dateT_x=(LCD.LCDWIDTH-len(dateT) * 6) / 2
			draw.text((lcdWidth,3),sayT,font=font)
			draw.text((ip_x,16),ip,font=font)
			draw.text((dateT_x-12,26),dateT, font=font)
			draw.text((62,26),str(temper)+u'℃', font=font)
			ISOTIMEFORMAT='%H:%M:%S'
			timeT=time.strftime(ISOTIMEFORMAT, time.localtime())
			timeT_x=(LCD.LCDWIDTH-len(timeT) * 6) / 2
			draw.text((timeT_x,36),timeT, font=font)
			disp.image(image)
			disp.display()
			lcdWidth-=11
			#print lcdWidth, LCD.LCDWIDTH
			if lcdWidth == -81:
				lcdWidth = LCD.LCDWIDTH
		time.sleep(1)

if __name__ == '__main__':
	reload(sys)  
	sys.setdefaultencoding('utf8')

	init()

	thread.start_new_thread(getIPThread,())
	thread.start_new_thread(getTemperature,())
	thread.start_new_thread(showStatus,())
	while True:

		connection,address = sock.accept()
		data = connection.recv(1024)
		if data:
			print "data size:%d" %len(data)
			print "data:%s" %data
			dataList = data.split("m")
			print dataList
			if dataList[0] == "1":
				msg = '给' + dataList[2] + '发送消息：'+ dataList[1]
				#msg = msg.decode('utf-8')
				print chardet.detect(msg)
				showMsg(msg)
			if dataList[0] == "2":
				msg = dataList[1]
				showMsg(msg)
			if dataList[0] == "3":
				msg = dataList[1]
				showMsg(msg)
			if dataList[0] == "4":
				msg = dataList[1]
				sayT = msg.decode("utf-8")
				lcdWidth = LCD.LCDWIDTH
			data = None

		time.sleep(0.2)
