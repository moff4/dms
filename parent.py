import sys
import time

import conf
class parent_class:
	def __init__(self):
		pass

	def log(self,msg):
		msg = "%s -:- %s "%(time.ctime(),msg)
		if '--no-stdout' not in sys.argv[1:]:
			print(msg)
		if '--no-log' not in sys.argv[1:]:
			open(conf.log_filename,'a').write(msg + '\n')

	def debug(self,msg):
		if '--debug' in sys.argv[1:]:
			print('DEBUG: %s'%str(msg))

	def extra(self,msg):
		if '--extra-output' in sys.argv[1:]:
			print('extra: %s'%str(msg))

