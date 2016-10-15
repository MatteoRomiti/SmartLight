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
saving = 0
week_day = [9,9,10,10,10,10,9,7,3,5,7,8,3,2,4,4,8,6,4,4,4,4,4,5]
week_end = [6,6,6,8,9,9,9,9,8,8,6,5,5,5,5,5,5,8,8,8,6,5,5,5]
week_day_tmp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
week_end_tmp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
update_done = 1
week_number = date.today().isocalendar()[1]

def get_presence():
	url="https://dweet.io/get/latest/dweet/for/presence"
	response = urllib2.urlopen(url)
	output = response.read()
	js = json.loads(output)
	return js["with"][0]["content"]["status"]

def do_mean():
	global week_day_tmp
	global week_day
	global week_end_tmp
	global week_end

	hours = range(0,24)
	for i in hours :
		week_day[i] = (week_day[i]+week_day_tmp[i]/5)/2
		week_end[i] = (week_end[i]+week_end_tmp[i]/2)/2
	week_day_tmp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	week_end_tmp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	return 

def update_statistics():
	global week_day_tmp
	global week_day
	global week_end_tmp
	global week_end
	global update_done
	global week_number

 	week_number_tmp = date.today().isocalendar()[1]

 	if week_number_tmp != week_number:
 		do_mean()
 		week_number = week_number_tmp
	day = datetime.datetime.today().weekday()+1
	now = datetime.datetime.now()
	hour = now.hour

	if day <= 5:
		week_day_tmp[hour] = week_day_tmp[hour]+1
	else:
		week_end_tmp[hour] = week_end_tmp[hour]+1

def delay():
	global week_day
	global week_end
	day = datetime.datetime.today().weekday()+1
	now = datetime.datetime.now()
	hour = now.hour
	# in a real case, num should be around 200
	num = 50
	if day <= 5:
		return num/week_day[hour]
	else:
		return num/week_end[hour]

def start_saving():
	value = "1"
	fp = open("saving.txt", 'w')								
	fp.write(value)
	fp.close()
	return "saving"

def end_saving():
	value = "0"
	fp = open("saving.txt", 'w')								
	fp.write(value)
	fp.close()
	return "not saving"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe([("sensor/presence", 2),("sensor/ext_light", 2),("web_switch/current_status", 2)])

def on_message(client, userdata, msg):
	global current_status
	global presence
	global ext_light
	global src
	global saving

	if msg.topic == "web_switch/current_status":
		d = json.loads(msg.payload)
		current_status = d["e"][0]["v"]
		src = d["e"][0]["source"]
		print "status received: " + current_status

	if msg.topic == "sensor/presence":
		d = json.loads(msg.payload)
		presence = d["e"][0]["v"]
		if presence == "1":
			update_statistics()
			if saving == 1: # if the light has been switched off because someone forgot it
				res = end_saving() # now someone is in the room, so we are not responsible for the saved energy anymore
				print res 
				saving = 0
		print "presence: " + presence

	if msg.topic == "sensor/ext_light":
		d = json.loads(msg.payload)
		ext_light = d["e"][0]["v"]
		print "external light : " + ext_light

	# control.py acts only if the light is on
	if current_status == "1":

		if src == "switch": # the user clicked on the web switch
			time.sleep(3) # wait few seconds to show that the switch is working, then check if the light can be on
			src = "default"
		
		# check if there's someone and the external light is not enough
		if presence == "0" or ext_light > "5": 
			if presence == "0": # do not switch off the light immediately, the user could be back soon
				n = delay() # waiting time based on the time and the day of the week
				print "sleep for : "+ str(n)
			 	time.sleep(n)
			 	print "end of sleep"
			 	presence = str(get_presence())
			 	print "presence: " + presence
			 	if presence == "0": # after n seconds the user is not back, so switch off the light
		 			command = "0"
		 			client.publish("web_switch/next_status", command)
		 			# now we save energy
		 			saving = 1
		 			res = start_saving() # write on ThingSpeak
					print res + " started"
					current_status = command
					print "command to switch off sent at " + str(int(time.time()))

	print "current_status:" + str(current_status) +"ext_light: " + str(ext_light)+ "presence: "+ str(presence)	

control = mqtt.Client("control", False)
control.on_connect = on_connect
control.on_message = on_message
control.connect("localhost")
control.loop_forever()