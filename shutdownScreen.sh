#!/bin/bash
listen_pid=`ps -ef | grep -v 'grep' |grep msgDisplay.py | awk '{print $2}'`
kill $listen_pid
