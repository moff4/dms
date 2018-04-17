#!/usr/bin/env python3.6
import sys
import os
import time
import json

from server import Server
import encrypt
import conf

HELP_MSG = '''
                                +-----------+                                 .
                                |  D  M  S  |
                                +-----------+

                       Decentralized Messaging System
    $ python3.6 main.py <Command> [ <Flag> ]
    
    Command:
      --init
          Создает необходимые директории и необходимые файлы кроме пары 
          ключей пользователя

      --gen-keypair
          Генерирует новую пару ключей

      --registrate
          Регистрирует пользователя на удаленном сервере

      --self-registrate
          Регистрирует пользователя, как первый блок в БД

      --upd-blckchn=<host>:<port>
          Обновить базу данных (блокчейн) от конкретного узла. При этом 
          необходимо использовать -k для указания публичного ключа узла -l для
          указания логина узла

      --server
          Запсутить сервер

    Flags:
      -h | --help
          Увидеть это сообщение еще раз

      -k <key filename>
          Использовать ключ из конкретного файла. Цель использования явно 
          зависит от <Command>

      -l <login>
          Использовать конкретный логин. Цель использования явно зависит 
          от <Command>

      --no-stdout
          Не выводить лог в stdout

      --no-log
          Не записывать лог в logfile

      --client
          Запустить дополнительно клиентскую часть
      
      --debug
          Отладочная печать

      --extra-output
          Выводить больше данных

    src: https://bitbicket.org/riniyar8/dms.git
'''

def generate_pair():
	priv,pub = encrypt.generate_RSA_key()
	priv,pub = encrypt.export_keys(priv,pub)
	open(conf.key_dir + json.load(open(conf.conf_dir + conf.conf_main))['private_key'],'wb').write(priv)
	open(conf.key_dir + json.load(open(conf.conf_dir + conf.conf_main))['public_key'],'wb').write(pub)

def init():
	for i in [conf.conf_dir,conf.blockchain_dir,conf.key_dir]:
		try:
			os.mkdir(i)
		except Exception as e:
			print('ERROR: making directory %s : %s'%(i,e))
	time.sleep(1)
	username = input('\nYour new login:')
	open(conf.conf_dir + conf.conf_main,'w').write(json.dumps({
			"username":username,
			"public_key":"%s.pub"%(username),
			"private_key":"%s.priv"%(username)
		}))


def main():
	sv = Server('full-load')
	sv.run()

if __name__ == '__main__':
	if ('-h' in sys.argv[1:]) or ('--help' in sys.argv[1:]):
		print(HELP_MSG)
	elif '--gen-keypair' in sys.argv[1:]:
		generate_pair()
	elif '--server' in sys.argv[1:]:
		main()
	elif '--registrate' in sys.argv[1:]:
		Server().registrate()
	elif '--self-registrate' in sys.argv[1:]:
		print('Success: %s'%Server().self_registrate())
	elif len(list(filter(lambda x:x.startswith('--upd-blckchn='),sys.argv[1:])))>0:
		Server().upd_blockchain(list(filter(lambda x:x.startswith('--upd-blckchn='),sys.argv[1:]))[0][len('--upd-blckchn='):].split(':'))
	elif '--init' in sys.argv[1:]:
		init()
	else:
		print('ERROR: expected command. Try -h for more info')