#!/usr/bin/env python

"""
	SSL Rest server that works with the iftt webservice "maker channel".
	This server requires you to provide your own ssl cert/key and a user
	key for user authentication.  If this server does not find a user key
	in the config file (config.json), it will create one.  

	IFTT payload is as follows:

	{
		"userKey" : "ABCDEF1234567890",
		"deviceName" : "BedRoomLight",
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


