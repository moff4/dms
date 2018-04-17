
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512,SHA256,MD5

#
# Generate pare of RSA keys
# return ( private , public )
#
def generate_RSA_key(x=4096):
	private_key = RSA.generate(x)
	public_key  = private_key.publickey()
	return (private_key,public_key)

#
# export keys
# return ( private , public ) # both bytes
# in case of error return None , None
#
def export_keys(private_key,public_key):
	try:
		return ( private_key.exportKey('PEM') , public_key.exportKey('PEM') )
	except:
		return None , None

#
# export single (any) key
# get RSA.keyobj , return bytes
# or None in case of error
#
def export_key(key):
	try:
		return key.exportKey('PEM')
	except:
		return False

#
# import keys
# return ( private , public ) # both RSA.keyobj
# in case of error raise Exception
#
def import_keys(private_filename,public_filename):
	private = RSA.importKey(open(private_filename).read())
	public  = RSA.importKey(open(public_filename).read())
	return private , public

#
# import public key from str
# return RSA.keyobject
# in case of error raise Exception
#
def import_public_key_from_str(public_key):
	return RSA.importKey(public_key)

#
# decrypt message using private_key
#
def decrypt_data(private_key,message):
	cipher = PKCS1_OAEP.new(private_key)
	res = cipher.decrypt(message)
	return res

#
# encrypt message_in_bytes using public_key
#
def encrypt_data(public_key,message_in_bytes):
	cipher = PKCS1_OAEP.new(public_key)
	ciphertext = cipher.encrypt(message_in_bytes)
	return ciphertext

#
# return signature of data
#
def data_to_signature(private_key,data):
	return private_key.sign(data,'')

#
# decrypt signature and return data
#
def verify_signature(public_key,signature,expected_msg):	 	
	return public_key.verify(expected_msg, signature)

#
# md5 hash
#
def md5(bytes_data):
	h = MD5.new()
	h.update(bytes_data)
	return h.hexdigest()

#
# sha256 hash
#
def sha256(bytes_data):
	h = SHA256.new()
	h.update(bytes_data)
	return h.hexdigest()

#
# sha512 hash
#
def sha512(bytes_data):
	h = SHA512.new()
	h.update(bytes_data)
	return h.hexdigest()