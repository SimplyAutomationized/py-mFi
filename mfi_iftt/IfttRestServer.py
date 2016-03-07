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


from mfi.MFiDiscovery import MFiDiscovery

class mFiDeviceWrapper(Resource):
	def __init__(self, device, key="TESTKEY"):
		self.device = device
		self.key = key
		self.queue = asyncio.Queue()

		self.loop = asyncio.get_event_loop()
		self.loop.create_task(self.parseMsg())

	def render_POST(self, httprequest):
		print("POST request")
		body = httprequest.content.read()

		print("POST body: {}".format(body))

		try:
			msg = json.loads(body)
			self.queue.put_nowait(msg)
		except:
			print("malformed body")
			return "malformed body.  body must be json"

		return ""

		
	@asyncio.coroutine
	def parseMsg(self):
		print("parseMsg started")
		try:
			while True:

				msg = yield asyncio.From(self.queue.get())

				print("got msg!!! {}".format(msg))

				if not "userKey" in msg or not "command" in msg:
					print("userKey and/or command missing")
					continue

				key = msg["userKey"]

				if key != self.key:
					print("invalid key")
					print("my key is: ", self.key)
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
		print("GET request")
		r = {"hello" : "world"}

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

	def openPort(self):
		try:
			import gi
			gi.require_version('GUPnPIgd', '1.0')
			from gi.repository import GLib, GUPnPIgd
			

			my_ip = "192.168.1.40"

			igd = GUPnPIgd.SimpleIgd()

			main = GLib.MainLoop()

			def mep(igd, proto, eip, erip, port, localip, lport, msg):
			    if port == self.port:
			    	print("port opened successfully!")
			        main.quit()

			igd.connect("mapped-external-port", mep)
			
			#igd.add_port("PROTO", EXTERNAL_PORT, INTERNAL_IP, INTERNAL_PORT, LEASE_DURATION_IN_SECONDS, "NAME")
			igd.add_port("TCP", self.port, my_ip, self.port, 0, "iftt_mfi")

			main.run()
		except:
			import sys, traceback
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
			traceback.print_exception(exc_type, exc_value, exc_traceback,
					limit=2, file=sys.stdout)


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

	try:
		from Crypto.Hash.SHA256 import SHA256Hash as sha256
	except:
		from hashlib import sha256 
		
	from binascii import hexlify

	s = sha256()
	s.update(str(random.getrandbits(numBits)))
	return hexlify(s.digest())

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('port', help="port", default=8096, nargs="?")
	parser.add_argument('--config', help='config', default='config.json')
	parser.add_argument('--upnp', help='use upnp to open port',action = 'store_true')

	args = parser.parse_args()

	loop = asyncio.get_event_loop()

	with open(args.config, "r") as configFile:
		config = json.loads(configFile.read())

	userKey = ""

	if not "userKey" in config:
		"generate a key and write it to the config file"
		userKey = generateKey(256)
		config["userKey"] = userKey

		with open(args.config, "w") as cf:
			cf.write(json.dumps(config, sort_keys=True, indent=4, separators=(', ', ': ')))
	else:
		userKey = config["userKey"]

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

	discover = MFiDiscovery()

	"try to discover all the devices"
	loop.run_until_complete(asyncio.sleep(10))

	server = RestServer(port=args.port, userKey=userKey, useSsl=useSsl, keyPath=sslKey, certPath=sslCrt)

	devices = config["devices"]

	for d in devices:
		name = d["name"]
		port = d["port"]
		user = d["user"]
		passwd = d["pass"]
		
		for discovered in discover.devices:
			if discovered.device_name == name:
				print("found matching device: ", name)
				server.addDevice(discovered(discovered.address, port, user, passwd))

	if args.upnp:
		server.openPort()

	server.startInThread()

	loop.run_forever()

