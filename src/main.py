from conf import *
from DockerManager import DockerManager


#INITIAL GLOBAL VARIABLES

DOCKER_MANAGER = DockerManager()
NODE_LIST = DOCKER_MANAGER.nodes

def main():



	#THIS MAIN IS BEING USED FOR TESTING PURPOSES



	#USE NODE_LIST to interact with the different nodes
	rawTX = ''
	for i in NODE_LIST:

		#result = i.forceLinuxCommand('ls /home')

		#TEST BITCOIN CORE CALLS -- WORKING
		'''
		if i.implementation == 'bitcoind':
			result =  i.getBlockchainInfo()
			print('Node Name: ' + i.name + ' | Node implementation: ' + i.implementation)
			print(result['chain'])

			result = i.sendRawTransaction('0200000000010103b13e7b5c596858c2aa45e31f9fd8eee9ca72c29bebbaeb3abff6edcada5c770100000000d7d6d0800210270000000000002200200ac3d06c10f477f9a61b26dfaacea322092ee9ecad5c47252c6688d543fc9482268603000000000016001423b23606aedf19f4e6d19cd44274c0363f3d972a04004730440220417bf1591bb6273abb92055bcbd0b312679d95f250fda4c60ea5bfa584e207b9022039240299b27d713fbf663ef214b62b3720a2b2e0b47636630bf049cbac1ab3bb01483045022100fc27f3d3fb1043a19cf187481b6c7317e83402c1c484639f46d96ca709464ae80220610b7019094ec71d89094969d8405f3b4a3cb665a221877e037000e3b21187460147522102fea906d4718f8bcffc9c037fa3e737a59372b21e9881d6fcd011f65d5e2e5a2721031f024390005362c104cfc04c72d90fdeff04abe849d655560e05d2a48d083deb52ae75cd8d20')
			print(result)
		'''

		peerId = ''
		#TEST C-LIGHTNING CALLS -- WORKING
		if i.implementation == 'lightningd':
			result = i.getPeersIds()
			peerId = result[0]

		#TEST C-LIGHTNING CALLS RPC -- WORKING
		if i.implementation == 'lightningd':
			result = i.signLastTx(peerId)
			#print(result)
			rawTX = result
			
			
	#TEST BROADCAST COMMITMENT TRANSACTION -- WORKING
	for i in NODE_LIST:
		if i.implementation == 'bitcoind':
			print(rawTX)
			result = i.sendRawTransaction(rawTX)
			print(result)




if __name__ == "__main__":
	main()