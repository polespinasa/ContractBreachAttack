from nodes import *

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
