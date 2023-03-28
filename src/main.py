from conf import *
from dockerManager import dockerManager



def main():

	
	test = dockerManager()
	print(test.containerNames)

	command = test.runCommand('polar-n3-backend1', 'whoami')
	
	
	print(command)






if __name__ == "__main__":
	main()