#-*- coding:utf-8 -*-

import redis
import sys
con = redis.Redis(host='127.0.0.1', port=6379, db=0, password='627795061')
thresholdKey = "config:threshold"
modelKey = "config:model"
threshold = int(con.get(thresholdKey))
if sys.argv[1] == 'add':
	threshold += 500
	threshold = str(threshold)
	con.set(thresholdKey, threshold)
elif sys.argv[1] == "sub":
	if threshold >= 2500:
		threshold -= 500
		threshold = str(threshold)
		con.set(thresholdKey, threshold)
elif sys.argv[1] == "off":
	con.set(modelKey, "offline")
else:
	con.set(modelKey, "online")

