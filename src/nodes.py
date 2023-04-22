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











