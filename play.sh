text=$1
token=$2
online=$3
echo $online
if [ "$online" -eq "1" ];
	then
	url="http://tsn.baidu.com/text2audio?tex= $text &lan=zh&cuid=dlSwkVT56CHwmnZHA4fy3UGj&ctp=1&tok=$token"
	wget -c "$url" -O /root/pyaudio/audio/audio.mp3 
	mplayer /root/pyaudio/audio/audio.mp3 
	rm /root/pyaudio/audio/audio.mp3
	echo 1
else
	/root/linux_voice/bin/tts_sample $text
	mplayer /root/pyaudio/audio/tts_sample.wav
	rm /root/pyaudio/audio/tts_sample.wav
	echo 2
fi

