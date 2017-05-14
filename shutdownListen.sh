#!/bin/bash
listen_pid=`ps -ef | grep -v 'grep' |grep listenCall.py | awk '{print $2}'`
kill $listen_pid
