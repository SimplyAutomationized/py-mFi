#!/usr/bin/env python

"""
	SSL Rest server that works with the iftt webservice "maker channel".
	This server requires you to provide your own ssl cert/key and a user
	key for user authentication.  If this server does not find a user key
	in the config file (config.json), it will create one.

	Server is organized as mfi devices as leaves.  For example, the device
	"FooSwitch" would be accessible via the url:

	https://server.com/FooSwitch

	IFTT payload is as follows:

	{
		"userKey" : "ABCDEF1234567890",
		"command" : {
			"name" : "dim",
			"value" : 50
		}
	}

	Possible commands:

	dim (value)

		dim light to value (0-100)


	output (value)

		set output on or off (True/False)
"""

import json
from threading import Thread
from twisted.internet import reactor, ssl, protocol
from twisted.web.server import Site
from twisted.web.resource import Resource
from datetime import datetime
import trollius as asyncio


from MSwitch import MSwitch

class mFiDeviceWrapper(Resource):
	def __init__(self, device, key="TESTKEY"):
		self.device = device
		self.key = key
		self.queue = asncio.Queue

		self.loop = asyncio.get_event_loop()
		self.loop.create_task(self.parseMsg())

	def render_POST(self, httprequest):
		body = httprequest.content.read()

		try:
			msg = json.loads(body)
		except:
			print("malformed body")
			return

			self.queue.put(msg)

	@asyncio.coroutine
	def parseMsg(self):

		try:
			while True:

				msg = yield asyncio.From(self.queue.get())

				if not "userKey" in msg or not "command" in msg:
					print("userKey and/or command missing")
					continue

				key = msg["userKey"]

				if key != self.key:
					print("invalid key")
					continue

				try:
					cmd = msg["command"]["name"]
					value = msg["command"]["value"]
				except KeyError:
					print("missing command/name or command/value keys")
					continue
				
				if cmd == "dim":
					if value < 0 or value > 100:
						print("invalid value")
						continue

					self.device.dimmer_level = value

				elif cmd == "output":
					if value.__class__ != bool:
						print("output value must be bool")
						continue

					self.device.output = value

		except:
			import sys, traceback
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
			traceback.print_exception(exc_type, exc_value, exc_traceback,
					limit=2, file=sys.stdout)
			print("Error with {0}".format(self.__name__))

				


	def render_GET(self, httprequest):
		r = {}

		replyData = json.dumps(r)
		httprequest.setHeader('Content-Type', 'application/json;charset=UTF-8')
		httprequest.setHeader('Content-Length', str(len(replyData)))

		return replyData

class Root(Resource):
	def __init__(self, userKey):
		Resource.__init__(self)
		self.devices = []
		self.userKey = userKey
		
	def addDevice(self, device):
		print("adding resource: {0}".format(device.device_name))
		dev = None
		for d in self.devices:
			if d.device_name == device.device_name:
				dev = d
		if not dev:
			dev = mFiDeviceWrapper(device, self.userKey)
			self.devices.append(dev)

		dev.addResource(device)

		self.putChild(device.device_name, dev)

	def getChild(self, name, request):
		print("root child requested: {0}".format(name))

		if name == '':
			return self
		return Resource.getChild(self, name, request)

	def render_POST(self, request):
		print("POST requested")
		rs = {}
		rs["devices"] = []

		for device in self.devices:
			rs['devices'].append(device.device_name)

		reply = json.dumps(rs)
		return reply

	def render_GET(self, request):
		print("root GET requested")
		rs = {}
		rs["devices"] = []

		print ("self.device: {0}".format(len(self.devices)))

		for device in self.devices:
			rs['devices'].append(device.device_name)

		reply = json.dumps(rs)
		return reply

class RestServer:

	def __init__(self, port = 8096, userKey="TESTKEY", useSsl = False, keyPath='server.key', certPath='server.crt'):
		self.root = Root(userKey)
		self.useSsl = useSsl
		self.addDevice = self.root.addDevice
		self.port = port
		self.serverKey = keyPath
		self.cert = certPath

	def run(self, signals = 1):
		print("Starting server")

		self.web = Site(self.root)
		if self.useSsl:
			self.contextFactory = ssl.DefaultOpenSSLContextFactory(self.serverKey, self.cert)
			reactor.listenSSL(self.port, self.web, self.contextFactory)
		else:
			reactor.listenTCP(self.port, self.web)

		if not signals:
			reactor.run(installSignalHandlers=signals)
		else:
			reactor.run()


	def startInThread(self):
		self.t = Thread(target=self.run, args=[0])
		self.t.daemon = True
		self.t.start()

def generateKey(numBits):
	"try to better randomization if available"
	try:
		from rdrand import RdRandom
		random = RdRandom()
	except:
		try:
			from Crypto.Random import random
		except:
			from random import random
		
	return random.getrandbits(numBits)

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('port', help="port", default=8096, nargs="?")
	parser.add_argument('--config', help='config', default='config.json')

	args = parser.parse_args()

	with open(args.config, "r") as configFile:
		config = json.loads(configFile.read())

	userKey = ""

	if not "userKey" in config:
		"generate a key and write it to the config file"
		userKey = generateKey(50)
		config["userKey"] = userKey

		with open(args.config, "w") as cf:
			cf.write(json.dumps(config, sort_keys=True, indent=4, separators=(', ', ': ')))

	useSsl = True
	sslKey = ""
	sslCrt = ""

	if not "sslKey" in config or not "sslCrt" in config:
		useSsl = False
	else:
		sslKey = config["sslKey"]
		sslCrt = config["sslCrt"]

	port = args.port

	if "port" in config:
		port = config["port"]

 	server = RestServer(port=args.port, userKey=userKey, useSsl=useSsl, keyPath=sslKey, certPath=sslCrt)

	devices = config["devices"]

	for d in devices:
		addy = d["address"]
		port = d["port"]
		user = d["user"]
		passwd = d["pass"]
		devtype = d["type"]

		if devtype == "switch":
			device = MSwitch(addy, port, user, passwd)
			server.addDevice(device)

	server.startInThread()

	asyncio.get_event_loop().run_forever()

