import paho.mqtt.client as mqtt
import time
import random
import cherrypy
import urllib2
import datetime

host = "localhost"
presence_input = mqtt.Client("presence_input")
presence_input.connect(host)
presence_input.loop_start()

url = "https://dweet.io/dweet/for/presence?status="

while True:
	presence=raw_input("presence = ")
	ts = int(time.time())
	senml = '{"bn": "Presence Sensor", "bt": "' + str(ts) + '", "e": [{"n": "Presence", "u": "Boolean", "v": "' + str(presence) + '"}]}'
	presence_input.publish("sensor/presence", senml)
	ts = int(time.time())
	print "published at: " + str(ts) + " and now I sleep 2 seconds"
	url_tmp = url + presence
	response = urllib2.urlopen(url_tmp)
	time.sleep(2)
