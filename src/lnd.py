from nodes import *


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
