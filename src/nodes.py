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


	def forceLinuxCommand(self, command, user=''):
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

		res, exit_code = self.manager.runCommand(self.name, command, user)

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

		self.__basicCommand = 'lightning-cli --network=regtest '
		self.id = self.__getID()

	
	def __getID(self):
		'''
		get node ID

		
		Args:

		Returns:
			string: ID in string format

		'''

		command = self.__basicCommand + 'getinfo'
		res = json.loads(self.forceLinuxCommand(command, CLIGHTNING_USER))
		
		return res['id']


	def getPeersIds(self):
		'''
		gets all peers IDs
	
		Args:

		Returns:
			list: list with all peer IDs

		''' 
		command = self.__basicCommand + 'listchannels'
		
		out = self.forceLinuxCommand(command,user=CLIGHTNING_USER)
		channels = json.loads(out)['channels']
		res = []
		for channel in channels:
			if channel['source'] != self.id and channel['source'] not in res:
				res.append(channel['source'])
			elif channel['destination'] != self.id and channel['destination'] not in res:
				res.append(channel['destination'])

		return res


	def signLastTx(self, peerID):
		'''
		sign last transaction from a channel specified

		Args:
			peerID str: ID of the channel peer

		Return:
			str: raw transaction signed
		'''

		command = self.__basicCommand + 'dev-sign-last-tx ' + peerID
		out = self.forceLinuxCommand(command, user=CLIGHTNING_USER)
		res = json.loads(out)['tx']
		
		return res
		



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
			str: transaction hash in hex
			
		'''

		command = self.__basicCommand + 'sendrawtransaction ' + raw
		res = self.forceLinuxCommand(command)
		return res

