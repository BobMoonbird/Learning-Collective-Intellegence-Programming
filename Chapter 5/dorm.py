import random, math
from optimization import randomOptimize, hillclimb, randomStartHillClimb, simulatedAnnealing, geneticOptimize

# Each dorm has two bedrooms
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']
prefs = [('Toby', ('Bacchus', 'Hercules')),
		 ('Steve', ('Zeus', 'Pluto')),
		 ('Andrea', ('Athena', 'Zeus')),
		 ('Sarah', ('Zeus', 'Pluto')),
		 ('Dave', ('Athena', 'Pluto')),
		 ('Jeff', ('Hercules', 'Pluto')),
		 ('Fred', ('Pluto', 'Athena')),
		 ('Suzie', ('Bacchus', 'Hercules')),
		 ('Laura', ('Bacchus', 'Hercules')),
		 ('Neil', ('Hercules', 'Athena'))]

domain = [(0, 2*len(dorms)-1-i) for i in range(len(dorms)*2)]

def printSolution(sol):
	slots = []
	for i in range(len(dorms)):
		slots += [i, i]
	for i in range(len(sol)):
		student = int(sol[i])
		dorm = dorms[slots[student]]
		print prefs[i][0], dorm
		del slots[student]

def dormCost(sol):
	cost = 0
	slots = []
	for i in range(len(dorms)):
		slots += [i, i]
	for i in range(len(sol)):
		student = int(sol[i])
		dorm = dorms[slots[student]]
		pref = prefs[i][1]
		if dorm == pref[0]: continue
		elif dorm == pref[1]: cost += 1
		else: cost += 3
		del slots[student]
	return cost

if __name__ == '__main__':
	sol = randomOptimize(domain, dormCost)
	print 'RandomOptimize'
	print 'Cost: ', dormCost(sol)
	printSolution(sol)
	print '------------------------------'
	sol = hillclimb(domain, dormCost)
	print 'HillClimb'
	print 'Cost: ', dormCost(sol)
	printSolution(sol)
	print '------------------------------'
	sol = randomStartHillClimb(domain, dormCost)
	print 'RandomStartHillClimb'
	print 'Cost: ', dormCost(sol)
	printSolution(sol)
	print '------------------------------'
	sol = simulatedAnnealing(domain, dormCost)
	print 'SimulatedAnnealing'
	print 'Cost: ', dormCost(sol)
	printSolution(sol)
	print '------------------------------'
	sol = geneticOptimize(domain, dormCost)
	print 'GeneticOptimize'
	print 'Cost: ', dormCost(sol)
	printSolution(sol)
	print '------------------------------'