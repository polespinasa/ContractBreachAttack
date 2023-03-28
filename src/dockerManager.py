import docker



class dockerManager:
	'''
	The dockerManager object contains info about the docker actual environment and running containers for the scenario specified
	
	Args:
		polarEnv (int): Define the polarEnv attribute value

	Attributes:
		polarEnv (int): The polarEnv is used to define the Polar scenario chosen, Polar separates different scenario containers with a number
		client (docker.client.DockerClient): The client is used for interfacing with docker
		containerNames (list): List of all container names in the scenario chosen

	''' 


	def __init__(self, polarEnv):

		self.polarEnv = str(polarEnv)
		self.client = docker.from_env()
		self.containerNames = self.__takeContainerNames()
		

	def __takeContainerNames(self):
		'''
		Take all the container names currently working on the declared Polar scenario

		Args: 

		Returns:
			list: container names
		'''

		container_list = self.client.containers.list()
		res = []
		for i in range(len(container_list)):
			name = self.client.containers.get(container_list[i].id).attrs['Name']
			
			#avoid taking containers from other polar scenarios
			if name[1:9] == 'polar-n' + self.polarEnv:
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

		if name not in self.containerNames:
			raise Exception("Container name must be in the containerNames list")
		return self.client.containers.get(name)


	def runCommand(self, name, command):
		'''
		Run a defined command into the container specified

		Args:
			name (str): container name
			command (str, list): command or commands to be executed

		Raises:
			Exception: Command is not in the container $PATH variable
			Exception: Command does not exist in the bitcoin-cli command catalog

		Returns:
			str: output of the command
		'''

		container = self.__getContainer(name)
		commandResult = container.exec_run(command)
		
		if commandResult.exit_code == 126:
			raise Exception("Command not found in the container $PATH")
		
		elif commandResult.exit_code == 89:
			raise Exception("Command not found in the bitcoin-cli command list")
		

		commandOutput = commandResult.output
		return commandOutput.decode()
