#!/usr/bin/env python3.6
import sys
import socket
import threading as th
import time
import json
import random
import binascii as asc

import encrypt
from parent import parent_class
from history import History
from blockchain import Block,Blockchain
import conf		

class Server(parent_class):
	def __init__(self,load_mode='demo'):
		super(Server, self).__init__()
		self.threads = []
		self.open_port()

		#
		# user keys
		#
		mcfg = json.load(open(conf.conf_dir + conf.conf_main))
		self.my_name = mcfg['username']
		try:
			self.private,self.public = encrypt.import_keys(conf.key_dir+mcfg['private_key'],conf.key_dir+mcfg['public_key'])
		except Exception as e:
			self.log('cannot find keys: (%s, %s) %s'%(conf.key_dir+mcfg['private_key'],conf.key_dir+mcfg['public_key'],e))
			sys.exit()


		#
		# runtime tables:
		# current active connections
		#
		self.__client_socket  = {} 
		self.__socket_clinet  = {}
		
		#
		# databes of existing users and their keys
		#
		self.blockchain = Blockchain()

		self.network_state = 0
		if load_mode == 'full-load':
			self.history = History()

	def __del__(self):
		try:
			self.socket.close()
		except:
			pass


	def generate_body_id(self):
		def random_item(az):
			i = int(random.random()*(len(az)-1))
			return az[i]
		CHARS =  ''
		for i in ( range(65,91) + range(48,58) + range(97,123) ):
			CHARS += chr(i)
		st = ''
		for i in range(10):
			st += random_item(CHARS)
		return st

	#
	# create listening socket
	#
	def open_port(self):
		port = conf.port
		host = '' # here we can make some restrictions on connections # but we will not
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((host, port))
		self.socket.listen(5)
		self.socket.settimeout(30*3600)


	def check_threads(self):
		if len(self.threads) <= 0:
			return
		i = 0
		while i < len(self.threads):
			if not self.threads[i].is_alive():
				self.threads.pop(i).join()
			else:
				i += 1

	#######################################
	##    FIRST LEVEL OF DMS PROTOCOL    ##
	#######################################
	#
	# low-level send msg
	#
	def __send(self,sock,msg,pub_key):
		max_size = 500
		if type(msg) == str:
			msg = msg.decode()
		if len(msg) <= max_size:
			msg = [encrypt.encrypt_data(pub_key,msg)]
		else:
			n = int(len(msg) / max_size) + 1
			_msg = []
			for i in range(n+1):
				st = ''
				for k in range(max_size):
					if len(msg) > 0:
						st += msg.pop(0)
					else:
						break
				if len(st)>0:
					_msg.append(encrypt.encrypt_data(pub_key,st))
			msg = msg
		query = ''
		for i in range(len(msg)):
			query += asc.b2a_base64(str(len(msg[i])).encode())[:-1] 
			if i == len(msg):
				query += b','
			else:
				query += b'.'
			query += msg[i]
		self.debug('send: %s'%query)
		sock.send(query)

	#
	# low-level recv msg 
	#
	def __recv(self,sock,priv_key):
		query = b''
		q = b''
		boo = True
		while boo:
			while q not in [b'.',b',']:
				q = sock.recv(1)
				query += q
			boo = q == b','
			msg = sock.recv(int(asc.a2b_base64(encrypt.decrypt_data(priv_key,query[:-1])).decode()))
		self.debug('recv: %s'%msg)
		return msg

	#######################################
	##   SECOND LEVEL OF DMS PROTOCOL    ##
	#######################################

	#
	# takes dict (2lv), covert to str , crypt
	# and send it to peer
	#
	def send_2lv(self,transport_message):
		peer = transport_message['to']
		if self.blockchain.peer_status(peer) != None: 
			pub = self.blockchain.get_key(peer)
			self.__send(json.dumps(transport_message).encode())
			return True
		else:
			return False

	#
	# recv msg from peer & decrypt it 
	# return transport-message (dict)
	#
	def recv_2lv(self,conn):
		try:
			transport_message = json.loads(self.__recv(conn,self.private))
			return transport_message
		except Exception as e:
			self.log('ERROR: recv_2lv: %s'%e)


	######################################
	##   THIRD LEVEL OF DMS PROTOCOL    ##
	######################################

	
	#
	# takes pub-key and dict , convert to str , encrypt using pub-key , decode to str and return str
	#
	def __3lv_crypt(self,pub,dd):
		res = asc.b2a_base64(encrypt.encrypt_data(pub,json.dumps(dd)))
		if type(res) == bytes:
			res = res.decode()
		return res
	
	#
	# takes str in base64 , encode , decrypt , convert to dict
	#
	def __3lv_norm(self,st):
		if type(st) == str:
			st = st.encode()
		res = encrypt.decrypt_data(self.private,asc.a2b_base64(st))
		if type(res) == bytes:
			res = res.decode()
		return json.loads(res)

	#
	# return True if msg send
	# or False in case of error
	#
	def __send_3lv_(self,peer,body_obj):
		if self.blockchain.exists(peer):
			pub = self.blockchain.get_key(peer)
			body_obj['sign'] = encrypt.data_to_signature(self.private,encrypt.md5(json.dumps(body_obj)))
			self.__3lv_crypt(pub,body_obj)
			obj = {
				'from':self.my_name,
				'to':peer,
				'flow-controll':(self.network_state << 2),
				'data':[body_obj]
			}
			return self.send_2lv(obj)
		else:
			return False

	#
	# registrate new user
	#
	def registrate(self):
		username = self.my_name
		pass # FIXME

	# 
	# gets 2lv package and decide to reg or auth
	# return True if user authorized or registrated
	# or False in case of error
	# 
	def auth_ot_reg(self,data):
		return True # if he is not Vasya then we will not understand our reply
		
	#
	# send message to user
	#
	def send_user_message(self,username,message):
		bobj = {
			'part':conf.USER_PART_ID,
			'id':1,
			'data':{
				'from':self.my_name,
				'message':message
			}
		}
		self.__send_3lv_(username,bobj)

	def db_update_request(self,username):
		bobj = {
			'part':conf.BLCKCHN_PART_ID,
			'id':1, # ask for number of blocks and last hash
			'data':{
				'from':self.my_name
			}
		}
		self.__send_3lv_(username,bobj)

	#
	# handler for part of messages
	#
	def __3lv_error_part_handler(self,hightest_msg,body_id):
		self.log('ERROR: [%s] [errnum: %s] %s'%(hightest_msg['data']['from'],hightest_msg['data']['body_id'],hightest_msg['data']['error_num'],hightest_msg['data']['error_msg']))
	
	#
	# handler for part of messages
	#
	def __3lv_user_part_handler(self,hightest_msg,body_id):
		if hightest_msg['id'] == 1: # incoming message
			peer = hightest_msg['data']['from']
			msg  = hightest_msg['data']['message']
			self.extra('[%s][%s] %s -- NEW MSG -- %s'%(time.ctime(),body_id,peer,msg))
			reply = {
				'part':conf.USER_PART_ID,
				'id':1,
				'data':{
					'from':self.my_name,
					'body-id':body_id
				}
			}
			self.__send_3lv_(peer,reply)
		elif hightest_msg['id'] == 2: # delivered
			peer = hightest_msg['data']['from']
			bid  = hightest_msg['data']['body-id']
			self.extra('[%s][%s] %s -- MSG DELIVERED [%s] '%(time.ctime(),body_id,peer,bid))
		elif hightest_msg['id'] == 3: # delivered
			peer = hightest_msg['data']['from']
			bid  = hightest_msg['data']['body-id']
			self.extra('[%s][%s] %s -- MSG READ [%s] '%(time.ctime(),body_id,peer,bid))
	
	#
	# handler for part of messages
	#
	def __3lv_blckchn_part_handler(self,hightest_msg,body_id):
		reply = None
		peer = None
		if hightest_msg['id'] == 1: # ask for number of blocks and last hash
			peer = hightest_msg['data']['from']
			self.extra('[%s][%s] %s -- BLCKCHN 1 -- %s'%(time.ctime(),body_id,peer,msg))
			reply = {
				'part':conf.BLCKCHN_PART_ID,
				'id':2,
				'data':{
					'from':self.my_name,
					'count':self.blockchain.count(),
					'hash':self.blockchain.last_hash(),
				}
			}
		elif hightest_msg['id'] == 2: # we get number of blocks (count) and last hash (hash)
			peer = hightest_msg['data']['from']
			self.extra('[%s][%s] %s -- BLCKCHN 2 -- %s'%(time.ctime(),body_id,peer,msg))
			count 		= hightest_msg['data']['count'] 
			last_hash 	= hightest_msg['data']['last_hash']
			if count > self.blockchain.count():
				reply = { # ask for blocks
					'part':conf.BLCKCHN_PART_ID,
					'id':3 ,
					'data':{
						'from':self.my_name,
						'max':self.blockchain.count(),
						'min':count,
					}
				}
		elif hightest_msg['id'] == 3: # we get request for blocks from (min) till (max)
			peer = hightest_msg['data']['from']
			self.extra('[%s][%s] %s -- BLCKCHN 3 -- %s'%(time.ctime(),body_id,peer,msg))
			_min = hightest_msg['data']['min'] 
			_max = hightest_msg['data']['max']
			blocks = []
			for i in range(_min,_max):
				blocks.append(self.blockchain.blocks[i]._export())
			reply = { # ask for blocks
				'part':conf.BLCKCHN_PART_ID,
				'id':4,
				'data':{
					'from':self.my_name,
					'blocks':blocks
				}
			}
		elif hightest_msg['id'] == 4: # we get list of blocks
			peer = hightest_msg['data']['from']
			self.extra('[%s][%s] %s -- BLCKCHN 4 -- %s'%(time.ctime(),body_id,peer,msg))
			blocks = hightest_msg['data']['blocks'] 
			try:
				for i in blocks:
					blck = Block()
					blck._import(i)
					self.blockchain.add_block(blck)
			except Exception as e:
				self.log('ERROR : incoming blocks damaged %s'%e)
		if self.reply != None:
			self.__send_3lv_(peer,reply)
	
	#
	# handler for part of messages
	#
	def __3lv_login_key_service_handler(self,hightest_msg,body_id):
		reply = None
		peer = None
		if hightest_msg['id'] == 1: # registrate new user
			peer = hightest_msg['data']['from']
			key = encrypt.import_public_key_from_str(hightest_msg['data']['key'])
			if self.blockchain.add_new_user(hightest_msg['data']['key'],peer,self.my_name,self.private):
				reply = { # ask for blocks
					'part':conf.LOGIN_KEY_SERVICE,
					'id':2, # success ful result
					'data':{
						'from':self.my_name,
						'result':'success'
					}
				}
		if self.reply != None:
			self.__send_3lv_(peer,reply)
	#
	# handler for part of messages
	#
	def __3lv_vote_part_handler(self,hightest_msg,body_id):
		pass # FIXME
	
	#
	# handler for part of messages
	#
	def __3lv_sysctl_part_handler(self,hightest_msg,body_id):
		#
		# don't know why i create this handler ._.
		#
		pass # FIXME

	#
	# handler for body-object (b64,str)
	#
	def third_level_handler(self,_body_obj):
		body_id = None
		try:
			body_id = _body_obj['body-id']
			if self.history.exists(body_id):
				return
			self.history.add(body_id)
			body_obj = self.__3lv_norm(_body_obj['data'])
			if encrypt.verify_signature(self.blockchain.get_key(body_obj['from']),body_obj.pop('sign'),encrypt.md5(json.dumps(body_obj))):
				if body_obj['part']   == conf.ERROR_PART_ID:
					self.__3lv_error_part_handler(body_obj,body_id)
				elif body_obj['part'] == conf.USER_PART_ID:
					self.__3lv_user_part_handler(body_obj,body_id)
				elif body_obj['part'] == conf.LOGIN_KEY_SERVICE:
					self.__3lv_login_key_service_handler(body_obj,body_id)
				elif body_obj['part'] == conf.BLCKCHN_PART_ID:
					self.__3lv_blckchn_part_handler(body_obj,body_id)
				elif body_obj['part'] == conf.VOTE_PART_ID:
					self.__3lv_vote_part_handler(body_obj,body_id)
				elif body_obj['part'] == conf.SYSCTL_PART_ID:
					self.__3lv_sysctl_part_handler(body_obj,body_id)
			else:
				self.log('ERROR: incoming bobj verificetion failed')
		except Exception as e:
			self.log('ERROR: 3lv handler [%s] : %s'%(body_id,e))

	#####################################
	##              OTHERS             ##
	#####################################

	#
	#
	#
	def upd_blockchain(self,addr_info):
		host = addr_info[0]
		port = addr_info[1]
		args = sys.argv[1:]
		i = args.index('-k')
		if i <= 0:
			self.log('ERROR: upd-blckchn: expected \'-k\'')
			return
		pub = encrypt.import_public_key_from_str(open(args.pop(i)).read())
		i = args.index('-l')
		if i <= 0:
			self.log('ERROR: upd-blckchn: expected \'-l\'')
			return
		username = args.pop(i)
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.connect((host, port))
		self.__client_socket[username] = conn
		self.__socket_clinet[str(conn)]= username
		self.blockchain.user_keys[username] = pub
		self.blockchain.servers[user_keys] = [host,port]
		self.db_update_request(username)



	#
	# handle single connection
	#
	def connection_handle(self,conn,addr):
		self.log("%s _ %s"%(conn,addr))
		self.__socket_clinet[str(conn)] = None
		SHOULD_BE_OPENED = True
		while SHOULD_BE_OPENED:
			send_box = {}
			try:
				package = self.recv_2lv(conn) # Transport-Meesage
				_from	= package['from']
				_to		= package['to']
				_data	= package['data']
				_flow	= package['flow-controll']
				
				AUTH_REG = _flow % (2**0) > 0 # auth or registrate
				SHOULD_BE_OPENED = _flow % (2**1) == 0 # close connection
				if (_flow % (2**2+2**3)) >> 2 != self.network_state:
					pass # should do s0mething

				if AUTH_REG:
					AUTH_REG = not self.auth_ot_reg(_data)
				if AUTH_REG:
					if self.__socket_clinet[str(conn)] == None:
						self.__socket_clinet[str(conn)] = _from
						self.__socket_clinet[_from] = str(conn)
					for body_object in _data:
						data = body_object['data']
						to = body_object['to']
						if to == self.my_name:
							self.third_level_handler(data)
						else:
							if to not in send_box:
								obj = {
									'from':self.my_name,
									'to':to,
									'data':[body_object]
								}
								send_box[to] = obj
							else:
								send_box[to]['data'].append(body_object)
			except Exception as e:
				self.log('ERROR: handler <%s> %s'%(addr,e))
			finally:
				flow = 0x0C & _flow
				for to in send_box:
					package = send_box[to]
					package['flow'] = _flow
					self.send_2lv(package)
		conn.close()




	#
	# main loop
	# create lots of threads and listen to socket
	#
	# Магия (идиотизм) питона в том, что есть GIL
	# Из-за которого все потоки превращаются в корутины
	# (и лишь зря занимают записи в таблицах процессов в ядре ОС)
	#
	def run(self):
		self.mainloop = True
		if '--client' in sys.argv[1:]:
			self.fork_client()
		delay = conf.delay
		try:
			self.log('Starting working')
			while self.mainloop: # MAINLOOP
				try:
					
					conn , addr = self.socket.accept()
					#
					# check for len of self.threads and kill one in case of need
					#
					_t = th.Thread( target = self.connection_handle, args = [conn,addr] )
					_t.start()
					self.threads.append(_t)
					self.check_threads()

				except socket.timeout as e: # time to reopen port
					try:
						self.socket.close()
					except Exception as e:
						self.log('Err while opennig port')
						time.sleep(delay*5)
					finally:
						self.open_port()
				except Exception as e:
					self.log('mainloop: %s'%e)
				finally:
					time.sleep(delay)
		except KeyboardInterrupt as e:
			self.log('Finish working')
			self.blockchain.save()

	#####################################################
	##                 USERS INTERFACE                 ##
	#####################################################

	#
	# 
	#
	def self_registrate(self):
		username = self.my_name
		reg_data = {
			'type':'user',
			'name':username,
			'key':encrypt.export_key(self.public).decode(),
			'address':[conf.host,conf.port]
		} 
		self.blockchain.reset()
		return self.blockchain.add_my_block(Block(n=0,data=json.dumps(reg_data),prev_hash='',hash_type='md5'),username,self.private)

	#
	# here will be forked thread for working with user
	#
	def fork_client(self):
		def client(self):
			CMDS = '''ENTER COMMAND:\n0 - exit\n1 - send msg\n'''
			while True:
				try:
					cmd = int(input(CMDS))
					if cmd == 0:
						self.mainloop = False
						return
					elif cmd == 1:
						username = input('peer-name: ')
						msg = input('message: ')
						self.send_user_message(username,msg)
					else:
						raise RuntimeError('unknown command %s'%cmd)
				except Exception as e:
					self.log('ERROR client: %s'%e)
		_t = th.Thread(target=client,args=[self])
		_t.start()
		self.threads.append(_t)