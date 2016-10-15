import paho.mqtt.client as mqtt
import time
import random
import urllib2
import datetime

host = "localhost"
presence_pub = mqtt.Client("presence_pub")
presence_pub.connect(host)
presence_pub.loop_start()

last_presence = -1
url = "https://dweet.io/dweet/for/presence?status="

# probability density function based on the hour of the day
# week_day's and week_end's values consider a room at home, an office would have different numbers
def pdf(h,day):
	tmp = random.randint(1,10)
	week_day = [9,9,10,10,10,10,9,7,3,5,7,8,3,2,4,4,8,6,4,4,4,4,4,5] # threshold for presence, 10 = always absence, 1 = always presence
	week_end = [6,6,6,8,9,9,9,9,8,8,6,5,5,5,5,5,5,8,8,8,6,5,5,5]

	if day <= 5: # for weekday
		if tmp <= week_day[int(h)]:
			presence = 0
		else:
			presence = 1
	else: # for weekend
		if tmp <= week_end[int(h)]:
			presence = 0
		else:
			presence = 1
	return presence
 
 # different pdfs for different hours and days (month may be considered as well)
def get_presence():
	day = datetime.datetime.today().weekday()+1
	now = datetime.datetime.now()
	m = now.month
	h = now.hour
	presence = pdf(h,day) # presence = 0 => absence, presence = 1 => presence
	return presence

while True:
	presence = get_presence()
	if presence != last_presence:
		last_presence = presence
		ts = int(time.time())
		senml = '{"bn": "Presence Sensor", "bt": "' + str(ts) + '", "e": [{"n": "Presence", "u": "Boolean", "v": "' + str(last_presence) + '"}]}'
		presence_pub.publish("sensor/presence", senml)
		url_tmp = url + str(last_presence)
		response = urllib2.urlopen(url_tmp)

	time.sleep(20)