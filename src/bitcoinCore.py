from nodes import *


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