import sys
if sys.version_info >= (3,0):
	from .MPower import *
	from .MSwitch import *
	from .MFiDiscovery import *
	from .MFiRestClient import *

else:
	from MPower import *
	from MSwitch import *
	from MFiDiscovery import *
	from MFiRestClient import *
