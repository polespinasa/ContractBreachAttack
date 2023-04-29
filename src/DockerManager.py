from conf import *
from nodes import *
from coreLightning import *
from lnd import *
from eclair import *
from bitcoinCore import *
import docker


class DockerManager:
	'''
	The dockerManager object contains info about the docker actual environment and running containers for the scenario specified
	
	Args:
		polarEnv (int): Define the polarEnv attribute value

	Attributes:
		polarEnv (int): The polarEnv is used to define the Polar scenario chosen, Polar separates different scenario containers with a number
		client (docker.client.DockerClient): The client is used for interfacing with docker
		containerNames (list): List of all container names in the scenario chosen

	Raises:
		Exception: POLAR_SCENARIO is not an integer

	''' 


	def __init__(self, polarEnv=POLAR_SCENARIO):

		if not isinstance(polarEnv, int):
			raise Exception("POLAR_SCENARIO defined in conf.py must be an integer")

		self.__polarEnv = str(polarEnv)
		self.__client = docker.from_env()
		self.__containerNames = self.__takeContainerNames()
		self.nodes = self.__getNodes()
		

	def __takeContainerNames(self):
		'''
		Take all the container names currently working on the declared Polar scenario

		Args: 

		Returns:
			list: container names
		'''

		container_list = self.__client.containers.list()
		res = []
		for i in range(len(container_list)):
			name = self.__client.containers.get(container_list[i].id).attrs['Name']
			
			
			#avoid taking containers from other polar scenarios
			if name[1:9] == 'polar-n' + self.__polarEnv:
				res.append(name[1:])

		return res


	def __getContainer(self, name):
		'''
		Take the container object by name
		The name must be in the containerNames list

		Args:
			name (str): name of the container
		
		Raises:
			Exception: Container name is not in the containerNames list

		Returns:
			docker.models.containers.Container: container object
		'''

		if name not in self.__containerNames:
			raise Exception("Container name must be in the containerNames list")
		return self.__client.containers.get(name)


	def __getNodes(self):
		'''
		Create all node objects with their names and implementation versions

		Returns:
			list Nodes.Nodes: a list with all Node objects 
		'''

		res = []
		for i in self.__containerNames:
			nodeImplmentation = self.__getContainer(i).attrs['Args'][0]

			if nodeImplmentation == 'lightningd':
				node = CLightning(self, i, nodeImplmentation)
			elif nodeImplmentation == 'lnd':
				node = LND(self, i, nodeImplmentation)
			elif nodeImplmentation == 'bitcoind':
				node = BitcoinCore(self, i, nodeImplmentation)
			elif nodeImplmentation == 'polar-eclair':
				node = Eclair(self, i, nodeImplmentation)
			else:
				raise Exception(nodeImplmentation + " is not a valid node implementation")

			res.append(node)


		return res


	def runCommand(self, name, command, user):
		'''
		Run a defined command into the container specified

		Args:
			name (str): container name
			command (str, list): command or commands to be executed

		Returns:
			str: output of the command
			int: exit code of the command
		'''

		container = self.__getContainer(name)
		commandResult = container.exec_run(command,user=user)
		
		commandOutput = commandResult.output
		
		return commandOutput.decode(), commandResult.exit_code


	def pause(self, name):
		'''
		Pause a specific container

		Args:
			name(str): container name

		Returns:
			bool: True if was correctly paused

		'''

		container = self.__getContainer(name)

		try:
			container.pause()
		except:
			return False

		return True