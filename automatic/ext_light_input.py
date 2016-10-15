import paho.mqtt.client as mqtt
import time
import random
import cherrypy
import urllib2
import datetime

host = "localhost"
ext_light_input = mqtt.Client("ext_light_input")
ext_light_input.connect(host)
ext_light_input.loop_start()

hour = "8:00"
url = "https://dweet.io/dweet/for/external_light?status="

while True:
	ext_light=raw_input("external light = ")
	ts = int(time.time())
	senml = '{"bn": "External Light Sensor", "bt": "' + str(hour) + '", "e": [{"n": "Presence", "u": "Boolean", "v": "' + str(ext_light) + '"}]}'
	ext_light_input.publish("sensor/ext_light", senml)
	url_tmp = url+str(ext_light)
	response = urllib2.urlopen(url_tmp)
	time.sleep(2)