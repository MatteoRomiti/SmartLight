import json
import urllib2
import time
import paho.mqtt.client as mqtt

host = "localhost"
change_pub = mqtt.Client("change_pub")
change_pub.connect(host)
change_pub.loop_start()
 
url_change="https://dweet.io/get/latest/dweet/for/automatic_switch"
last_update = "default"
i = 0 # just to avoid to publish the I time (old values)
fail = 0

while True:
	response = urllib2.urlopen(url_change)
	output = response.read()
	js = json.loads(output)

	if js["this"] != "succeeded" and fail == 0 and i > 0:
		ts = int(time.time())
		senml = '{"bn": "Web-switch", "bt": "' + str(ts) + '", "e": [{"n": "Status", "u": "Boolean", "v": "change"}]}'
		change_pub.publish("web_switch/change_request", senml)
		print "change status request sent"
		fail = 1
	else:
		if js["this"] == "succeeded":
			if i > 0 :
				fail = 0 # two consecutive fails never occur
				t = js["with"][0]["created"]
				if str(t) != str(last_update) :
					ts = int(time.time())
				 	senml = '{"bn": "Web-switch", "bt": "' + str(ts) + '", "e": [{"n": "Status", "u": "Boolean", "v": "change"}]}'
				 	change_pub.publish("web_switch/change_request", senml)
				 	print "change status request sent"
					last_update = t
			last_update = js["with"][0]["created"]
	i = 1
	time.sleep(1)