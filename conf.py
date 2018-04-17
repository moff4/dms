##################################################
###              GENERAL SETTINGS              ###
##################################################
# host (str)
host 					=	'127.0.0.1'
# port (int)
port 					=	8080
# configuration dir (str)
conf_dir				=	'config/'
# main config with info about user account in JSON formate (str)
conf_main				=	'main.json'
# directory where will be stored all blocks for blockchain (str)
blockchain_dir			=	'blocks/'
# directory where should be keys (str)
key_dir					=	'keys/'
# log file name (str)
log_filename			=	'log/log.txt'
# in case of error ; the best is somewhere in (0.1,1.0) (float)
delay					=	0.5

##################################################
###               EXTRA SETTINGS               ###
##################################################
# timeout in seocnds between cleaning history for old objids (float)
History_clean_timeout	=	2.0
# how long in seconds we should keep objids in history
History_duration		=	24*3600

##################################################
###           PROTOCOL CONFIGURATIONS          ###
##################################################
# error-part-id (int)
ERROR_PART_ID			=	0
# user-part-id (int)
USER_PART_ID			=	1
# login-key-service (int)
LOGIN_KEY_SERVICE		=	2
# blockchain-part-id (int)
BLCKCHN_PART_ID			=	3
# vote-part-id (int)
VOTE_PART_ID			=	4
# syscontroll-part-id
SYSCTL_PART_ID			=	5