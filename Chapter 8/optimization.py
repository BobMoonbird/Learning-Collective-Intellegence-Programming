import time, random, math

people = [('Seymour', 'BOS'), 
		  ('Franny', 'DAL'), 
		  ('Zooey', 'CAK'),
		  ('Walt', 'MIA'), 
		  ('Buddy', 'ORD'), 
		  ('Les', 'OMA')]
destination = 'LGA'

def getMinutes(t):
	res = time.strptime(t, '%H:%M')
	return res[3]*60 + res[4]

def printSchedule(schedule):
	for d in range(len(schedule) / 2):
		name = people[d][0]
		origin = people[d][1]
		out = flights[(origin, destination)][schedule[2*d]]
		ret = flights[(destination, origin)][schedule[2*d+1]]
		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % \
			  (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2])

def scheduleCost(sol):
	totalprice = 0
	latestArrival = 0
	earliestDepart = 24*60
	for d in range(len(sol) / 2):
		origin = people[d][1]
		out = flights[(origin, destination)][int(sol[2*d])]
		ret = flights[(destination, origin)][int(sol[2*d+1])]
		totalprice += out[2] + ret[2]
		if latestArrival < getMinutes(out[1]): latestArrival = getMinutes(out[1])
		if earliestDepart > getMinutes(ret[0]): earliestDepart = getMinutes(ret[0])
	totalwait = 0
	for d in range(len(sol) / 2):
		origin = people[d][1]
		out = flights[(origin, destination)][int(sol[2*d])]
		ret = flights[(destination, origin)][int(sol[2*d+1])]
		totalwait += latestArrival - getMinutes(out[1])
		totalwait += getMinutes(ret[0]) - earliestDepart
	if latestArrival < earliestDepart:
		totalprice += 50
	return totalprice + totalwait

def randomOptimize(domain, costf=scheduleCost, guess=1000):
	bestCost = 999999999
	bestSol = None
	for i in range(guess):
		randomSol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		cost = costf(randomSol)
		if cost < bestCost:
			bestCost = cost
			bestSol = randomSol
	return bestSol

def hillclimb(domain, costf=scheduleCost):
	sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
	while True:
		neighbors = []
		for j in range(len(domain)):
			if sol[j] > domain[j][0]:
				neighbors.append(sol[:j] + [sol[j]-1] + sol[j+1:])
			if sol[j] < domain[j][1]:
				neighbors.append(sol[:j] + [sol[j]+1] + sol[j+1:])
		currCost = costf(sol)
		bestCost = currCost
		for neighbor in neighbors:
			cost = costf(neighbor)
			if cost < bestCost:
				bestCost = cost
				sol = neighbor
		if bestCost == currCost:
			break
	return sol

def randomStartHillClimb(domain, costf=scheduleCost, trial=100):
	bestSol = None
	bestCost = 999999999
	for _ in range(trial):
		sol = hillclimb(domain, costf)
		cost = costf(sol)
		if cost < bestCost:
			bestCost = cost
			bestSol = sol
	return bestSol

def simulatedAnnealing(domain, costf=scheduleCost, T=10000.0, coolingRate=0.99, step=3):
	sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
	currCost = costf(sol)
	while T > 0.1:
		idx = random.randint(0, len(domain) - 1)
		delta = random.randint(-step, step)
		updateVal = min(max(sol[idx] + delta, domain[idx][0]), domain[idx][1])
		newSol = sol[:idx] + [updateVal] + sol[idx+1:]
		nextCost = costf(newSol)
		if (nextCost < currCost or random.random() < 1.0*pow(math.e, -1.0*(nextCost - currCost)/T)):
			sol = newSol
			currCost = nextCost
		T = T * coolingRate
	return sol

def geneticOptimize(domain, costf=scheduleCost, popsize=50, step=1, mutprob=0.2, elite=0.2, maxiter=100):
	def mutate(sol):
		idx = random.randint(0, len(domain) - 1)
		if random.random() < 0.5:
			return sol[:idx] + [max(sol[idx] - step, domain[idx][0])] + sol[idx+1:]
		else:
			return sol[:idx] + [min(sol[idx] + step, domain[idx][1])] + sol[idx+1:]
	def crossover(sol1, sol2):
		idx = random.randint(1, len(domain) - 2)
		return sol1[:idx] + sol2[idx:]
	population = []
	for i in range(popsize):
		sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		population.append(sol)
	topelite = int(elite * popsize)
	for i in range(maxiter):
		scores = [(costf(s), s) for s in population]
		scores = sorted(scores)
		ranked = [sol for (s, sol) in scores]
		population = ranked[:topelite]
		while len(population) < popsize:
			if random.random() < mutprob:
				c = random.randint(0, topelite)
				population.append(mutate(ranked[c]))
			else:
				c1 = random.randint(0, topelite)
				c2 = random.randint(0, topelite)
				population.append(crossover(ranked[c1], ranked[c2]))
	return scores[0][1]


if __name__ == '__main__':
	fp = open('schedule.txt', 'r')
	flights = {}
	for line in fp:
		origin, dest, depart, arrive, price = line.strip().split(',')
		flights.setdefault((origin, dest), [])
		flights[(origin, dest)].append((depart, arrive, int(price)))
	domain = [(0, 9)] * (len(people) * 2)
	# sol = randomOptimize(domain, guess=1000)
	# print 'Random optimization', scheduleCost(sol), sol
	# printSchedule(sol)
	# print '---------------------------------'
	# sol = hillclimb(domain)
	# print 'Hillclime optimization', scheduleCost(sol), sol
	# printSchedule(sol)
	# print '---------------------------------'
	# sol = randomStartHillClimb(domain)
	# print 'RandomStartHillClimb optimization', scheduleCost(sol), sol
	# printSchedule(sol)
	# print '---------------------------------'
	# sol = simulatedAnnealing(domain)
	# print 'Simulated Annealing optimization', scheduleCost(sol), sol
	# printSchedule(sol)
	# print '---------------------------------'
	sol = geneticOptimize(domain)
	print 'Genetic optimization', scheduleCost(sol), sol
	printSchedule(sol)



