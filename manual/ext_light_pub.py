import paho.mqtt.client as mqtt
import time
import json
import urllib2

host = "localhost"
ext_light_pub = mqtt.Client("ext_light_pub")
ext_light_pub.connect(host)
ext_light_pub.loop_start()

h = 0
url = "https://dweet.io/dweet/for/external_light?status="

def get_ext_light(h):
	time = str(h) + ":00"
	fp = open("sunny_day.txt")
	d = json.loads(fp.read())
	return time, d[time]

while True:
	if h == 24:
		h = 0
	else:
		hour, ext_light = get_ext_light(h)
		ts = int(time.time())
		senml = '{"bn": "External Light Sensor", "bt": "' + str(hour) + '", "e": [{"n": "Presence", "u": "Boolean", "v": "' + str(ext_light) + '"}]}'
		ext_light_pub.publish("sensor/ext_light", senml)
		url_tmp = url+str(ext_light)
		response = urllib2.urlopen(url_tmp)
		h += 1
		time.sleep(20)