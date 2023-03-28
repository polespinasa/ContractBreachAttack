from conf import *
from dockerManager import dockerManager



def main():

	
	test = dockerManager(POLAR_SCENARIO)
	print(test.containerNames)

	command = test.runCommand('polar-n3-backend1', 'whoami')
	
	
	print(command)






if __name__ == "__main__":
	main()