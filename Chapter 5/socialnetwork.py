import math
from optimization import randomOptimize, hillclimb, randomStartHillClimb, simulatedAnnealing, geneticOptimize
import Image, ImageDraw

people = ['Charlie','Augustus','Veruca','Violet','Mike','Joe','Willy','Miranda']

links = [('Augustus', 'Willy'), 
        ('Mike', 'Joe'), 
        ('Miranda', 'Mike'), 
        ('Violet', 'Augustus'), 
        ('Miranda', 'Willy'), 
        ('Charlie', 'Mike'), 
        ('Veruca', 'Joe'), 
        ('Miranda', 'Augustus'), 
        ('Willy', 'Augustus'), 
        ('Joe', 'Charlie'), 
        ('Veruca', 'Augustus'), 
        ('Miranda', 'Joe')]
domain = [(10, 370) for i in range(len(people) * 2)]

def crossCount(v):
	total = 0.0
	loc = dict([(people[i], (v[2*i], v[2*i+1])) for i in range(len(people))])
	for i in range(len(links)):
		for j in range(i + 1, len(links)):
			if isIntersected(loc[links[i][0]], loc[links[i][1]], loc[links[j][0]], loc[links[j][1]]):
				total += 1.0
	for i in range(len(people)):
		for j in range(i+1, len(people)):
			(x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]
			dist = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
			if dist < 50:
				total += 1.0 - dist/50.0
	return total

def isIntersected(p1, p2, p3, p4):
	(x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
	den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
	if den == 0: return False
	ua = 1.0 * ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
	ub = 1.0 * ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
	if ua > 0 and ua < 1 and ub > 0 and ub < 1:
		return True
	return False

def drawNetwork(sol):
	img = Image.new('RGB', (400, 400), (255, 255, 255))
	draw = ImageDraw.Draw(img)
	pos = dict([(people[i], (sol[2*i], sol[2*i+1])) for i in range(len(people))])
	for (a, b) in links:
		draw.line((pos[a], pos[b]), fill=(255, 0, 0))
	for n, p in pos.iteritems():
		draw.text(p, n, (0, 0, 0))
	img.show()

if __name__ == '__main__':
	bestSol = None
	best = 10
	for _ in range(100):
		sol = simulatedAnnealing(domain, crossCount, step=1, coolingRate=0.99)
		if crossCount(sol) < best:
			best = crossCount(sol)
			bestSol = sol
	print best
	drawNetwork(bestSol)

	

