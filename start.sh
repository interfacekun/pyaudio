#!/bin/bash
nohup python /root/pyaudio/listenCall.py > /dev/null 2>&1  &
python /root/pyaudio/showMsg.py 4m等待语音输入
