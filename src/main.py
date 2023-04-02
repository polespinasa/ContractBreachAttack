from conf import *
from DockerManager import DockerManager
from datetime import datetime


#INITIAL GLOBAL VARIABLES

DOCKER_MANAGER = DockerManager()
NODE_LIST = DOCKER_MANAGER.nodes

def main():

	#SIMPLE CONTRACT BREACH ATTACK SIMULATION


	# 1. Identify all nodes and save in easy variables to use
	for i in NODE_LIST:
		if i.implementation == 'lnd':
			victim = i
		elif i.implementation == 'lightningd':
			malicious = i
		else:
			bitcoin_core = i


	
	# 2. Initialize the results file
	date = datetime.now()
	file_name = str(date.day) + '_' + str(date.month) + '_' + str(date.hour) + str(date.minute) + str(date.second) + '.txt'
	f = open(file_name, "w")
	f.write("SIMULTAION TIME " + str(date) +'\n')


	### MAYBE CREATE A CLASS THAT DOES ALL THIS JOB AUTOMATICALLY
	victimBalance = 10045
	maliciousBalance = 239955
	f.write("INITIAL STATE:\n")
	f.write("Victim balance: " + str(victimBalance) + '\n')
	f.write("Malicious balance: " + str(maliciousBalance) + '\n')

	
	# 3. Malicious pays 100k sats to victim

	invoice = victim.createInvoice(100000)
	res = malicious.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance += 100000
	maliciousBalance -= 100000
	f.write("\n\nMalicious pays 100k sats to victim")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")


	# 4. Victim pays 50k sats to malicious
	invoice = malicious.createInvoice(50000)
	res = victim.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance -= 50000
	maliciousBalance += 50000
	f.write("\n\nVictim pays 50k sats to malicious")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	

	# 5. Malicious save this commitment transaction
	peerId = malicious.getPeersIds()[0]
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	#6. Malicous pays 40k sats to victim
	invoice = victim.createInvoice(40000)
	res = malicious.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance += 40000
	maliciousBalance -= 40000
	f.write("\n\nMalicious pays 50k sats to victim")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	

	#7. Malicious broadcast previous state
	res = bitcoin_core.sendRawTransaction(commitmentTx)
	f.write("\n\nMalicious broadcast previous state")
	f.write("  Commitment transaction in hex: \n  " + res)




if __name__ == "__main__":
	main()