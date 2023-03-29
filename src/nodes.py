import json
import ast
from conf import *


class Node:
	'''
	The node object is the main node class for all node implementations in polar
	
	Args:
		manager (dockerManager): manager is the dockerManager assigned to this node
		name (string): name of the node
		implementation (string): implementation type of the node

	Attributes:
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 


	''' 


	def __init__(self, manager, name, implementation):

		self.manager = manager
		self.name = name
		self.implementation = implementation


	def forceLinuxCommand(self, command):
		'''
		Run a linux command inside the node docker

		Args: 
			command (string): linux command that want to reun

		Raises:
			Exception: Command is not in the container $PATH variable
			Exception: Command does not exist in the bitcoin-cli command catalog
			Exception: Other errors

		Returns:
			string: output of that command
		'''

		res, exit_code = self.manager.runCommand(self.name, command)

		if exit_code == 126:
			raise Exception("Command not found in the container $PATH")
		
		elif exit_code == 89:
			raise Exception("Command not found in the bitcoin-cli command list")

		elif exit_code != 0:
			raise Exception(res)

		return res



class CLightning(Node):
	'''
	The CLightning object is used to interact with CLightning node implementations
	
	Args:
		Args used for Node Class

	Attributes:
		Attributes from Node Class

	''' 

	def __init__(self, manager, name, implementation):

		super(CLightning, self).__init__(manager, name, implementation)

		self.__basicCommand = 'curl localhost:8080/v1/'
		self.__macaroon = self.__getMacaroon()

	def __getMacaroon(self):
		'''
		gets macaroon and parses it into the correct format
	
		Args:

		Returns:
			str: macaroon in hex format

		''' 

		import binascii
		with open(MACAROON_PATH, 'rb') as f:
			macaroon = binascii.hexlify(f.read()).decode()

		return str(macaroon)
	

	def getPeersIds(self):
		'''
		gets all peers IDs
	
		Args:

		Returns:
			dict: a dict with all peer ids and node alias as keys

		''' 
		command = self.__basicCommand + 'peer/listpeers -s --header "Content-Type: application/json" --header "encodingtype: hex" --header "macaroon: '+ self.__macaroon + '"'
		
		res = json.loads(self.forceLinuxCommand(command))

		peersId = {}
		for peer in res:
			peersId[peer['alias']] = peer['id']
		
		return peersId


	######################## NOT WORKING YET #####################
	def signLastTx(self):


		data = '{"method": "getinfo"}'
		command = self.__basicCommand + 'rpc -s -X POST -d "method=getinfo" -v --header "Content-Type: application/json" --header "encodingtype: hex" --header "macaroon: ' + self.__macaroon + '"'
		print(self.forceLinuxCommand(command))
		exit(1)
		res = json.loads(self.forceLinuxCommand(command))
		print(res)
		



class LND(Node):
	'''
	The LND object is used to interact with LND node implementations
	
	Args:
		Args used for Node Class

	Attributes:
		Attributes from Node Class

	''' 
	def __init__(self, manager, name, implementation):

		super(LND, self).__init__(manager, name, implementation)



class BitcoinCore(Node):
	'''
	The BitcoinCore object is used to interact with BitcoinCore node implementations
	
	Args:
		Args used for Node Class

	Attributes:
		Attributes from Node Class

	''' 
	def __init__(self, manager, name, implementation):

		super(BitcoinCore, self).__init__(manager, name, implementation)

		self.__basicCommand = 'bitcoin-cli -regtest -rpcport=18443 -rpcuser=polaruser -rpcpassword=polarpass '


	def getBlockchainInfo(self):
		'''
		gets Blockchain actual information
	
		Args:

		Returns:
			dict: all information from blockchain in dictionary format

		''' 

		command = self.__basicCommand + 'getblockchaininfo'
		res = self.forceLinuxCommand(command)
		jsonres = json.loads(res)

		return jsonres


	def sendRawTransaction(self, raw):
		'''
		gets Blockchain actual information
	
		Args:
			raw (str): raw transaction to braodcast in string format

		Returns:
			str: resposta del node
			
		'''

		command = self.__basicCommand + 'sendrawtransaction ' + raw
		res = self.forceLinuxCommand(command)
		return res


