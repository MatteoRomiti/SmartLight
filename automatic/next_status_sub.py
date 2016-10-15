import paho.mqtt.client as mqtt
import urllib2
import json
import time

# default value
current_status = "0"

def write_on_file(value):
	fp = open("status.txt", 'w')								
	fp.write(value)
	fp.close()
	return True

def write_on_url(url):
	response = urllib2.urlopen(url)
	output = response.read()
	js = json.loads(output)
	return js

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    next_status_sub.subscribe([("web_switch/next_status",2),("web_switch/change_request",2)])


def on_message(client, userdata, msg):
	global current_status

	if msg.topic == "web_switch/change_request":
		if current_status == "1":
			current_status = "0"
		else :
			current_status = "1"

		write_on_file(current_status)
		url = "https://dweet.io/dweet/for/light_automatic?status="
		url_tmp = url + str(current_status)
		js = write_on_url(url_tmp)
		
		while js["this"]=="failed":
			time.sleep(1)
			js = write_on_url(url_tmp)
			
		
		print "NEXT_STATUS_SUB:Status changed to " + str(js["with"]["content"]["status"]) + " (switch request)"#just to verify
		ts = int(time.time())
		senml = '{"bn": "Web-switch", "bt": "' + str(ts) + '", "e": [{"n": "Status", "source" : "switch", "u": "Boolean", "v":"' + str(js["with"]["content"]["status"])+'"}]}'
		next_status_sub.publish("web_switch/current_status", senml)


	if msg.topic == "web_switch/next_status":
		print "next status received at " + str(int(time.time()))
		next_status = msg.payload
		write_on_file(next_status)
		url="https://dweet.io/dweet/for/light_automatic?status="
		url_tmp = url + next_status
		js = write_on_url(url_tmp)
		
		while js["this"]=="failed":
			time.sleep(1)
			js = write_on_url(url_tmp)

		print "NEXT_STATUS_SUB:Status changed to " + str(js["with"]["content"]["status"]) + " (control request)"#just to verify
		ts = int(time.time())
		senml = '{"bn": "Web-switch", "bt": "' + str(ts) + '", "e": [{"n": "Status", "source" : "control", "u": "Boolean", "v":"' + str(js["with"]["content"]["status"])+'"}]}'
		next_status_sub.publish("web_switch/current_status", senml)
		current_status = next_status

next_status_sub = mqtt.Client("next_status_sub", False)
next_status_sub.on_connect = on_connect
next_status_sub.on_message = on_message
next_status_sub.connect("localhost")
next_status_sub.loop_forever()