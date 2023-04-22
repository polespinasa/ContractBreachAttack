from nodes import *


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