text=$1
token=$2
online=$3
key=$4
echo $online
if [ "$online" -eq "1" ]; then
	start_tm=`date +%s.%N`
	url="http://tsn.baidu.com/text2audio?tex= $text &lan=zh&cuid=dlSwkVT56CHwmnZHA4fy3UGj&ctp=1&tok=$token"
	wget -c -q "$url" -O /root/pyaudio/audio/audio.mp3 
	end_tm=`date +%s.%N`
	use_tm=`echo $end_tm $start_tm | awk '{ print ($1 - $2)}'`
	echo "com use_tm:"$use_tm
	play -q /root/pyaudio/audio/audio.mp3
	python /root/pyaudio/showMsg.py '4m等待语音输入'
	rm /root/pyaudio/audio/audio.mp3
	echo 1
elif [ "$online" -eq "2" ]; then
	playFile="/root/pyaudio/audio/"$key
	if [ -f "$playFile" ]; then
		echo "$playFile"" exist"
		play -q $playFile
		python /root/pyaudio/showMsg.py '4m等待语音输入'
	else
		url="http://tsn.baidu.com/text2audio?tex= $text &lan=zh&cuid=dlSwkVT56CHwmnZHA4fy3UGj&ctp=1&tok=$token"
		wget -c -q "$url" -O $playFile 
		end_tm=`date +%s.%N`
		use_tm=`echo $end_tm $start_tm | awk '{ print ($1 - $2)}'`
		echo "com use_tm:"$use_tm
		play -q $playFile
		python /root/pyaudio/showMsg.py '4m等待语音输入'
	fi
else
	start_tm=`date +%s.%N`
	/root/linux_voice/bin/tts_sample $text
	end_tm=`date +%s.%N`
	use_tm=`echo $end_tm $start_tm | awk '{ print ($1 - $2)}'`
	echo "com use_tm:"$use_tm
	play -q /root/pyaudio/audio/tts_sample.wav
	python /root/pyaudio/showMsg.py '4m等待语音输入'
	rm /root/pyaudio/audio/tts_sample.wav
	echo 2
fi
