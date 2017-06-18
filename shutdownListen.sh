#!/bin/bash
listen_pid=`ps -ef | grep -v 'grep' |grep listenCall.py | awk '{print $2}'`
kill $listen_pid
python /root/pyaudio/showMsg.py '4m语音识别未启动'