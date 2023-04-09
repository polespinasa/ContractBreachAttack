import json
from conf import *
from time import time, sleep


class Node:
	'''
	The node object is the main node class for all node implementations in polar
	
	Args:
		manager (dockerManager): manager is the dockerManager assigned to this node
		name (string): name of the node
		implementation (string): implementation type of the node

	Attributes:
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 
		name (string): Node name following Polar name types
		implementation (string): description of the node implementation, can be; lightningd, lnd or bitcoind

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
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 
		name (string): Node name following Polar name types
		implementation (string): description of the node implementation, can be; lightningd, lnd or bitcoind


	Attributes:
		__basicCommand (str): basic command to use CLighting node
		id (str): pubkey identifier of the node
		__invoiceLabe (str): Unique label to be used when creating invoices

	''' 

	def __init__(self, manager, name, implementation):

		super(CLightning, self).__init__(manager, name, implementation)

		self.__basicCommand = 'lightning-cli --network=regtest '
		self.id = self.__getID()
		self.__invoiceLabel = str(time()).replace('.','') #Use timestamp as this has to be unique

	
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

	def getFundingTransactionID(self):
		'''

		Get funding transaction ID

		Returns:
			string: id of the funding transaction
		
		'''

		res = []
		command = self.__basicCommand + 'listpeers'
		out = self.forceLinuxCommand(command, user=CLIGHTNING_USER)
		res = json.loads(out)['peers'][0]['channels'][0]['funding_txid']
		
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


	def payInvoice(self, bolt11):
		'''
		Pay a bolt11 invoice

		Args:
			bolt11 str: Bolt11 invoice from the requester

		Return:
			bool: true if payment completed
		'''

		command = self.__basicCommand + 'pay ' + bolt11
		out = self.forceLinuxCommand(command, user=CLIGHTNING_USER)
		res = json.loads(out)['status']

		return res == 'complete'


	def createInvoice(self, ammount):
		'''
		Create bolt 11 invoice

		Args:
			ammount int: ammount to pay in satoshis

		Raises:
			Exception: if ammount in milisatoshis is equal or less than 0

		Return:
			str: bolt11 invoice
		'''
		
		if ammount == 0:
			raise Exception('Ammount must be bigger than 0')

		command = self.__basicCommand + 'invoice ' + str(ammount*1000) + ' ' + self.__invoiceLabel + ' simulationInvoice'
		output = self.forceLinuxCommand(command, user=CLIGHTNING_USER)
		res = json.loads(output)['bolt11']

		#increment label for the next invoice as has to be unique
		self.__invoiceLabel = str(int(self.__invoiceLabel) + 1)

		return res



class LND(Node):
	'''
	The LND object is used to interact with LND node implementations
	
	Args:
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 
		name (string): Node name following Polar name types
		implementation (string): description of the node implementation, can be; lightningd, lnd or bitcoind


	Attributes:
		__basicCommand (str): basic command to use CLighting node
		id (str): pubkey identifier of the node

	''' 

	def __init__(self, manager, name, implementation):

		super(LND, self).__init__(manager, name, implementation)
		self.__basicCommand = 'lncli --network regtest '
		self.id = self.__getID()


	def __getID(self):
		'''
		get node ID

		
		Args:

		Returns:
			string: ID in string format

		'''

		command = self.__basicCommand + 'getinfo'
		output = self.forceLinuxCommand(command, user=LND_USER)
		res = json.loads(output)['identity_pubkey']

		return res

	def getFundingTransactionID(self):
		'''

		Get funding transaction ID

		Returns:
			string: id of the funding transaction
		
		'''

		command = self.__basicCommand + 'listchannels'
		output = self.forceLinuxCommand(command, user=LND_USER)
		res = json.loads(output)['channels'][0]['channel_point'][:-2]

		return res


	def createInvoice(self, ammount):
		'''
		Create bolt 11 invoice

		Args:
			ammount int: ammount to pay in satoshis

		Raises:
			Exception: if ammount in milisatoshis is equal or less than 0

		Return:
			str: bolt11 invoice
		'''

		if ammount <= 0:
			raise Exception('Ammount must be bigger than 0')

		command = self.__basicCommand + 'addinvoice --amt=' + str(ammount)
		output = self.forceLinuxCommand(command, user=LND_USER)
		res = json.loads(output)['payment_request']

		return res


	def payInvoice(self, bolt11):
		'''
		Pay a bolt11 invoice

		Args:
			bolt11 str: Bolt11 invoice from the requester

		Return:
			bool: true if payment completed
		'''

		command = self.__basicCommand + 'sendpayment --pay_req=' + bolt11 + ' -f --json'
		output = self.forceLinuxCommand(command, user=LND_USER)
		res = json.loads(output)['status']

		return res == 'SUCCEEDED'


class Eclair(Node):
	'''
	The Eclair object is used to interact with Eclair node implementations
	
	Args:
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 
		name (string): Node name following Polar name types
		implementation (string): description of the node implementation, can be; lightningd, lnd or bitcoind


	Attributes:
		__basicCommand (str): basic command to use CLighting node
		id (str): pubkey identifier of the node

	''' 

	def __init__(self, manager, name, implementation):

		super(Eclair, self).__init__(manager, name, implementation)
		self.__basicCommand = 'eclair-cli -p eclairpw '
		self.id = self.__getID()


	def __getID(self):
		'''
		get node ID

		
		Args:

		Returns:
			string: ID in string format

		'''

		command = self.__basicCommand + 'getinfo'
		output = self.forceLinuxCommand(command, user=ECLAIR_USER)
		res = json.loads(output)['nodeId']

		return res

	def getFundingTransactionID(self):
		'''

		Get funding transaction ID

		Returns:
			string: id of the funding transaction
		
		'''

		command = self.__basicCommand + 'channels'
		output = self.forceLinuxCommand(command, user=ECLAIR_USER)
		res = json.loads(output)[0]['data']['commitments']['commitInput']['outPoint'][:-2]

		return res


	def createInvoice(self, ammount):
		'''
		Create bolt 11 invoice

		Args:
			ammount int: ammount to pay in satoshis

		Raises:
			Exception: if ammount in milisatoshis is equal or less than 0

		Return:
			str: bolt11 invoice
		'''

		if ammount <= 0:
			raise Exception('Ammount must be bigger than 0')

		command = self.__basicCommand + 'createinvoice --description=desc --amountMsat=' + str(int(ammount) * 1000)
		output = self.forceLinuxCommand(command, user=ECLAIR_USER)
		res = json.loads(output)['serialized']

		return res


	def payInvoice(self, bolt11):
		'''
		Pay a bolt11 invoice

		Args:
			bolt11 str: Bolt11 invoice from the requester

		Return:
			bool: true if payment completed
		'''

		command = self.__basicCommand + 'payinvoice --invoice=' + bolt11
		paymentID = self.forceLinuxCommand(command, user=ECLAIR_USER).strip()

		res = 'pending'
		
		while res == 'pending':
			command = self.__basicCommand + 'getsentinfo --id=' + paymentID
			output = self.forceLinuxCommand(command, user=ECLAIR_USER)
			res = json.loads(output)[0]['status']['type']
			sleep(1.5) 

		return res == 'sent'


class BitcoinCore(Node):
	'''
	The BitcoinCore object is used to interact with BitcoinCore node implementations
	
	Args:
		manager (dockerManager): The manager is the dockerManager object that interact directly with the docker container 
		name (string): Node name following Polar name types
		implementation (string): description of the node implementation, can be; lightningd, lnd or bitcoind


	Attributes:
		__basicCommand (str): basic command to use CLighting node
		defaultAddr (str): default address to claim block mining rewards
	'''

	def __init__(self, manager, name, implementation):

		super(BitcoinCore, self).__init__(manager, name, implementation)

		self.__basicCommand = 'bitcoin-cli -regtest -rpcport=18443 -rpcuser=polaruser -rpcpassword=polarpass '
		self.defaultAddr = self.getNewAddr()

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


	def getRawTransaction(self, txid):
		'''
		get raw transaction given a transaction id

		args:
			txid (str): id of the transaction

		returns:
			str: raw transaction
		'''

		command = self.__basicCommand + 'getrawtransaction ' + txid
		output = self.forceLinuxCommand(command)

		return output.strip()


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

	def getNewAddr(self):
		'''
		generate a new bitcoin address

		Returns:
			str: new address
		'''

		command = self.__basicCommand + 'getnewaddress'
		res = self.forceLinuxCommand(command)

		return res.strip()

	def mineNewBlocks(self, numBlocks=1, minerAddr=None):
		'''
		mine n num of new blocks

		Args:
			numBlocks (int/float): number of blocks to mine, 1 by default
			minerAddr (str): address that will be used to claim the block reward
		Raises:
			Exception: numBlocks is lower than 1
			Exception: numBlocks has decimals
			Exception: minerAddr is not a string

		Returns:
			list: list with the hashes of the mined blocks
		'''

		if numBlocks < 1:
			raise Exception("numBlocks to mine must minimum 1")
		if isinstance(numBlocks, float) and not numBlocks.is_integer():
			raise Exception("numBlocks must be an integer or a float with no decimals")

		if minerAddr == None:
			minerAddr = self.defaultAddr

		if not isinstance(minerAddr, str):
			raise Exception("minerAddr type must be a string")


		
		command = self.__basicCommand + 'generatetoaddress ' + str(numBlocks) + ' ' + minerAddr
		res = self.forceLinuxCommand(command)
		
		
		
		res = res.replace(' ', '').replace('\n','').replace('"','').replace('[','').replace(']','')
		res = list(map(str, res.split(',')))
		return res