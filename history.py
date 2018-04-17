#!/usr/bin/env python3.5
import time
import threading as th
import conf 
class History:
	def __init__(self):
		self.__history = {}
		self.__cleantime = conf.History_clean_timeout
		self.thread = None
		self.start()

	#
	# adds new objid or raise RuntimeError in case of error
	#
	def add(self,objid):
		if objid in self.__history:
			raise RuntimeError('objid already exists')
		else:
			self.__history[objid] = time.time()

	#
	# return True if objid already in history
	#
	def exists(self,objid):
		return objid in self.__history

	#
	# stop thread for cleaning history
	#
	def stop(self):
		if self.thread == None:
			raise RuntimeError('Cleaner should be started before stopping')
		self.__WORK = False
		self.thread.join()

	#
	# start thread for cleaning history
	#
	def start(self):
		self.__WORK = True
		self.thread = th.Thread(target=self.__filter,args=[])
		self.thread.start()

	#
	#
	#
	def __filter(self):
		def abs(x):
			if x < 0:
				return x * (-1)
			else:
				return x
		while self.__WORK:
			curr_time = time.time()
			for i in list(self.__history.keys()):
				if abs(self.__history[i] - curr_time) >= conf.History_duration:
					self.__history.pop(i)
			time.sleep(self.__cleantime)
			