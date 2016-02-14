import urllib
import urllib2
import json

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('address', help="address", default="localhost", nargs="?")
	parser.add_argument('port', help="port", default=8096, nargs="?")
	parser.add_argument('key', help="userKey", default="TESTKEY", nargs="?")
	parser.add_argument('device', help="device name to activate", default="mFi689981", nargs="?")
	parser.add_argument('--ssl', dest="useSsl", help="use ssl", action="store_true")
	args = parser.parse_args()

	usessl = ""

	if args.useSsl:
		usessl="s"

	url = 'http{}://{}:{}/{}'.format(usessl, args.address, args.port, args.device)

	print("url={}".format(url))

	values = {"userKey" : args.key, "command" : { "name" : "output", "value" : True }}

	#data = urllib.urlencode(json.dumps(values))
	data = json.dumps(values)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	the_page = response.read()

	print("the_page: {}".format(the_page))

