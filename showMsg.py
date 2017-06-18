#!/usr/bin/env python
#-*- coding:utf-8 -*-
import socket
import os
import time
import sys
import chardet

if __name__ == '__main__':
	reload(sys)  
	sys.setdefaultencoding('utf8')
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	conn = '/tmp/disMsg.txt'
	sock.connect(conn)
	msg = sys.argv[1]
	#msg = '4&'+msg+'&爸爸'
	sock.send(msg)
	sock.close()