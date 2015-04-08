import random, copy, math

######### Parse Tree Structure and Functions #########

class funcWrapper:

	def __init__(self, function, childcount, name):
		self.function = function
		self.childcount = childcount
		self.name = name

class funcNode:

	def __init__(self, fwrapper, children):
		self.function = fwrapper.function
		self.name = fwrapper.name
		self.children = children

	def evaluate(self, inp):
		results = [node.evaluate(inp) for node in self.children]
		return self.function(results)

	def display(self, intent=0):
		print ('  ' * intent) + self.name
		for node in self.children:
			node.display(intent + 1)

class paramNode:

	def __init__(self, index):
		self.index = index

	def evaluate(self, inp):
		return inp[self.index]

	def display(self, intent=0):
		print '%sparam%d' % ('  ' * intent, self.index)

class constNode:

	def __init__(self, val):
		self.val = val

	def evaluate(self, inp):
		return self.val

	def display(self, intent=0):
		print '%s%d' % ('  ' * intent, self.val)

addWrapper = funcWrapper(lambda x: x[0] + x[1], 2, 'add')
subtractWrapper = funcWrapper(lambda x: x[0] - x[1], 2, 'subtract')
multiplyWrapper = funcWrapper(lambda x: x[0] * x[1], 2, 'multiply')
ifWrapper = funcWrapper(lambda x: x[1] if x[0] > 0 else x[2], 3, 'if')
greaterWrapper = funcWrapper(lambda x: 1 if x[0] > x[1] else 0, 2, 'isGreater')

funcList = [addWrapper, subtractWrapper, multiplyWrapper, ifWrapper, greaterWrapper]


def exampleTree():
	return funcNode(ifWrapper, [funcNode(greaterWrapper, [paramNode(0), constNode(3)]),
								funcNode(addWrapper, [paramNode(1), constNode(5)]),
								funcNode(subtractWrapper, [paramNode(1), constNode(2)])])

def makeRandomTree(paramCount, maxDepth=4, funcProb=0.4, paramProb=0.6):
	if random.random() < funcProb and maxDepth > 0:
		func = random.choice(funcList)
		children = [makeRandomTree(paramCount, maxDepth - 1, funcProb, paramProb) for _ in range(func.childcount)]
		return funcNode(func, children)
	elif random.random() < paramProb:
		return paramNode(random.randint(0, paramCount-1))
	else:
		return constNode(random.randint(0, 10))

######### Genetic Function Evolution #########

def hiddenFunction(x, y):
	return x**2 + 2*y + 3*x + 5

def buildHiddenSet(func=hiddenFunction, size=200, maxLimit=40):
	rows = []
	for _ in range(200):
		x = random.randint(0, maxLimit)
		y = random.randint(0, maxLimit)
		rows.append([x, y, func(x, y)])
	return rows

def scoreFunction(tree, rows):
	assert tree
	diff = 0
	for row in rows:
		diff += abs(tree.evaluate([row[0], row[1]]) - row[2])
	return diff

def mutate(tree, paramCount, prob=0.1):
	if random.random() < prob:
		return makeRandomTree(paramCount)
	else:
		newTree = copy.deepcopy(tree)
		if isinstance(tree, funcNode):
			newTree.children = [mutate(child, paramCount, prob) for child in tree.children]
		return newTree

def crossover(tree1, tree2, prob=0.7, top=1):
	if random.random() < prob and not top:
		return copy.deepcopy(tree2)
	else:
		res = copy.deepcopy(tree1)
		if isinstance(tree1, funcNode) and isinstance(tree2, funcNode):
			res.children = [crossover(child, random.choice(tree2.children), prob, 0) for child in tree1.children]
		return res

def evolve(paramCount, popsize, rankf, maxgen=500, mutateRate=0.1, breedingRate=0.4, pexp=0.7, pnew=0.05, standard=0):
	def selectIndex():
		return int(math.log(random.random())/math.log(pexp))

	population = [makeRandomTree(paramCount) for _ in range(popsize)]
	scores = []
	for _ in range(maxgen):
		scores = rankf(population)
		print scores[0][0]
		if scores[0][0] <= standard: break
		newpop = [scores[0][1], scores[1][1]]
		while len(newpop) < popsize:
			if random.random() < pnew:
				newpop.append(makeRandomTree(paramCount))
			else:
				newpop.append(mutate(crossover(scores[selectIndex()][1], scores[selectIndex()][1], prob=breedingRate), paramCount, prob=mutateRate))
		population = newpop
	if len(scores) > 0: 
		return scores[0][1]
	return None

def getRankFunction(dataset, scoref=scoreFunction):
	def rankf(population):
		scores = [(scoref(tree, dataset), tree) for tree in population]
		scores.sort()
		return scores
	return rankf

######### Grid Game #########

def gridgame(players, maxstep=50):
	domain = [3, 3]
	lastmove = [-1, -1]
	location = [[random.randint(0, domain[0]), random.randint(0, domain[1])]]
	location.append([(location[0][0] + 2) % 4, (location[0][1] + 2) % 4])
	for _ in range(maxstep):
		for i in range(2):
			locs = location[i] + location[1-i]
			locs.append(lastmove[i])
			move = players[i].evaluate(locs) % 4
			if move == lastmove[i]: return 1-i
			lastmove[i] = move
			if move == 0:
				location[i][0] -= 1
				if location[i][0] < 0: location[i][0] = 0
			elif move == 1:
				location[i][0] += 1
				if location[i][0] > domain[0]: location[i][0] = domain[0]
			elif move == 2:
				location[i][1] -= 1
				if location[i][1] < 0: location[i][1] = 0
			elif move == 3:
				location[i][1] += 1
				if location[i][1] > domain[1]: location[i][1] = domain[1]
			if location[i] == location[1-i]:
				return i
	return -1

def tournament(players):
	losses = [0 for player in players]
	for i in range(len(players)):
		for j in range(len(players)):
			if i == j: continue
			winner = gridgame([players[i], players[j]])
			if winner == 0:
				losses[j] += 2
			elif winner == 1:
				losses[i] += 2
			else:
				losses[i] += 1
				losses[j] += 1
	scores = sorted(zip(losses, players))
	return scores

class humanplayer:

	def evaluate(self, board):
		me = tuple(board[0:2])
		others = [tuple(board[x:x+2]) for x in range(2, len(board) - 1, 2)]
		for i in range(4):
			for j in range(4):
				if (i, j) == me:
					print 'O',
				elif (i, j) in others:
					print 'X',
				else:
					print '-',
			print ''
		print 'Your last move was %d' % board[-1]
		print ' 0'
		print '2 3'
		print ' 1'
		print 'Enter move: '
		move = int(raw_input())
		return move



if __name__ == '__main__':
	# tree = makeRandomTree(2)
	# dataset = buildHiddenSet()
	# rankf = getRankFunction(dataset)
	# finalTree = evolve(2, 500, rankf, mutateRate=0.2, breedingRate=0.1, pexp=0.7, pnew=0.1)
	# if finalTree: finalTree.display()

	winner = evolve(5, 100, tournament, maxgen=50, mutateRate=0.2, breedingRate=0.1, pexp=0.9, pnew=0.01, standard=0)
	if winner: winner.display()
	print gridgame([winner, humanplayer()])
	





















