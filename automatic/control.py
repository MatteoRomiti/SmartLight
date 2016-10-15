import paho.mqtt.client as mqtt
import json
import time
import datetime
import urllib2
from datetime import date

#default values
presence = "-1"
ext_light = "-1"
current_status = "0"
src = "default"

def get_presence():
	url="https://dweet.io/get/latest/dweet/for/presence"
	response = urllib2.urlopen(url)
	output = response.read()
	js = json.loads(output)
	return js["with"][0]["content"]["status"]

def get_current_status():
	url = "https://dweet.io/get/latest/dweet/for/light_automatic"
	response = urllib2.urlopen(url)
	output = response.read()
	js = json.loads(output)
	return js["with"][0]["content"]["status"]

def get_ext_light():
	url = "https://dweet.io/get/latest/dweet/for/external_light"
	response = urllib2.urlopen(url)
	output = response.read()
	js = json.loads(output)
	return js["with"][0]["content"]["status"]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe([("sensor/presence", 2),("sensor/ext_light", 2),("web_switch/current_status", 2)])

def on_message(client, userdata, msg):
	global current_status
	global presence
	global ext_light
	global src

	if msg.topic == "web_switch/current_status":
		d = json.loads(msg.payload)
		current_status = d["e"][0]["v"]
		src = d["e"][0]["source"]
		print "status received: " + current_status

	if msg.topic == "sensor/presence":
		d = json.loads(msg.payload)
		presence = d["e"][0]["v"]
		print "presence: " + presence

	if msg.topic == "sensor/ext_light":
		d = json.loads(msg.payload)
		ext_light = d["e"][0]["v"]
		print "external light : " + ext_light

	if src == "switch":
		n = 6 # this could be an input from a form
		time.sleep(n) # for n seconds the user can do wathever he wants, then the system comes back to automatic mode
		src = "default"
		presence = str(get_presence())
		current_status = str(get_current_status())
		ext_light = str(get_ext_light())

	#check if there's someone and the external light is not enough
	if presence == "1" and ext_light < "5":
		command = "1"
	else:
		command = "0"
	print "command:" + command
	print "current status: " + current_status

	if current_status == command:
		print "The web switch is already " + command
	else:
		# send a command to change the status
		client.publish("web_switch/next_status", command)
		current_status = command
		print "A message has been sent to set the status to: " + current_status

	print "current_status:" + current_status + "ext_light: " + ext_light + "presence: " + presence	

control = mqtt.Client("control", False)
control.on_connect = on_connect
control.on_message = on_message
control.connect("localhost")
control.loop_forever()