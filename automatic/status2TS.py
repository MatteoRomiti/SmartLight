import time
import urllib2

while True:
	fp = open("status.txt")
	value = fp.read()
	field = "&field5=" # it depends on which field of your channel you want to write to
	write_key = "YJ355THRY4XEFB5C" # for my channel
	baseURL = 'https://api.thingspeak.com/update?api_key=' + write_key
	f = urllib2.urlopen(baseURL + field + value)
	print f.read() # 0 => writing failed, > 0 writing successful
	fp.close()
	time.sleep(15) # minimum time to wait to let ThingSpeak work