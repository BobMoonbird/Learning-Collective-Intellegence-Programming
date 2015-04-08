import math
from PIL import Image, ImageDraw

my_data = [['slashdot','USA','yes',18,'None'],
          ['google','France','yes',23,'Premium'],
          ['digg','USA','yes',24,'Basic'],
          ['kiwitobes','France','yes',23,'Basic'],
          ['google','UK','no',21,'Premium'],
          ['(direct)','New Zealand','no',12,'None'],
          ['(direct)','UK','no',21,'Basic'],
          ['google','USA','no',24,'Premium'],
          ['slashdot','France','yes',19,'None'],
          ['digg','USA','no',18,'None'],
          ['google','UK','no',18,'None'],
          ['kiwitobes','UK','no',19,'None'],
          ['digg','New Zealand','yes',12,'Basic'],
          ['slashdot','UK','no',21,'None'],
          ['google','UK','yes',18,'Basic'],
          ['kiwitobes','France','yes',19,'Basic']]


class decisionnode:
    
    def __init__(self, col=-1, value=None, results=None, truebranch=None, falsebranch=None):
        self.col = col
        self.value = value
        self.results = results
        self.truebranch = truebranch
        self.falsebranch = falsebranch

def divideSet(rows, column, value):
    splitFunction = None
    if isinstance(value, int) or isinstance(value, float):
        splitFunction = lambda row: row[column] >= value
    else:
        splitFunction = lambda row: row[column] == value
    set1 = [row for row in rows if splitFunction(row)]
    set2 = [row for row in rows if not splitFunction(row)]
    return (set1, set2)

def uniqueCounts(rows):
    res = {}
    for row in rows:
        r = row[-1]
        if r not in res: res[r] = 0
        res[r] += 1
    return res

def giniInpurity(rows):
    total = len(rows)
    counts = uniqueCounts(rows)
    imp = 0
    for k1 in counts:
        p1 = 1.0 * counts[k1] / total
        for k2 in counts:
            if k1 == k2: continue
            p2 = 1.0 * counts[k2] / total
            imp += p1 * p2
    return imp

def entropy(rows):
    total = len(rows)
    counts = uniqueCounts(rows)
    ent = 0.0
    for k in counts:
        p = 1.0 * counts[k] / total
        ent -= p * math.log(p, 2)
    return ent

def variance(rows):
    if len(rows) == 0: return 0
    data = [1.0 * row[-1] for row in rows]
    mean = sum(data) / len(data)
    var = sum([(d-mean)**2 for d in data])/len(data)
    return var

def buildtree(rows, scoreFunction=entropy):
    if len(rows) == 0: return decisionnode()
    currScore = scoreFunction(rows)

    bestGain = 0.0
    bestCriteria = None
    bestSets = None

    numOfCols = len(rows[0]) - 1
    for col in range(0, numOfCols):
        colValues = set()
        for row in rows:
            colValues.add(row[col])
        for value in colValues:
            set1, set2 = divideSet(rows, col, value)
            p = 1.0 * len(set1) / len(rows)
            gain = currScore - p * scoreFunction(set1) - (1-p) * scoreFunction(set2)
            if gain > bestGain and len(set1) > 0 and len(set2) > 0:
                bestGain = gain
                bestCriteria = (col, value)
                bestSets = (set1, set2)

    if bestGain > 0:
        truebranch = buildtree(bestSets[0])
        falsebranch = buildtree(bestSets[1])
        return decisionnode(col=bestCriteria[0], value=bestCriteria[1], truebranch=truebranch, falsebranch=falsebranch)
    else:
        return decisionnode(results=uniqueCounts(rows))

def printTree(tree, indent=' '):
    if tree.results != None:
        print tree.results
    else:
        print str(tree.col) + ':' + str(tree.value) + '? '
        print indent + 'T->',
        printTree(tree.truebranch, indent+' ')
        print indent + 'F->',
        printTree(tree.falsebranch, indent+' ')

def getWidth(tree):
    if tree.truebranch == None and tree.falsebranch == None: return 1
    else: return getWidth(tree.truebranch) + getWidth(tree.falsebranch)

def getDepth(tree):
    if tree.truebranch == None and tree.falsebranch == None: return 0
    else: return max(getDepth(tree.truebranch), getDepth(tree.falsebranch)) + 1

def drawTree(tree, jpeg='tree.jpg'):
    w = getWidth(tree) * 100
    d = getDepth(tree) * 100 + 120
    img = Image.new('RGB', (w, d), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    drawNode(draw, tree, w/2, 20)
    img.save(jpeg, 'JPEG')

def drawNode(draw, tree, x, y):
    if tree.results == None:
        w1 = getWidth(tree.falsebranch) * 100
        w2 = getWidth(tree.truebranch) * 100
        left = x - (w1 + w2) / 2
        right = x + (w1 + w2) / 2
        draw.text((x-20, y-10), str(tree.col) + ':' + str(tree.value) + '?', (0, 0, 0))
        draw.line((x, y, left+w1/2, y+100), (255, 0, 0))
        draw.line((x, y, right-w2/2, y+100), (255, 0, 0))
        drawNode(draw, tree.falsebranch, left+w1/2, y+100)
        drawNode(draw, tree.truebranch, right-w2/2, y+100)
    else:
        txt = '\n'.join(['%s:%d' % val for val in tree.results.iteritems()])
        draw.text((x-20, y), txt, (0, 0, 0))

def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v > tree.value: branch = tree.truebranch
            else: branch = tree.falsebranch
        else:
            if v == tree.value: branch = tree.truebranch
            else: branch = tree.falsebranch
        return classify(observation, branch)

def prune(tree, mingain):
    if tree.falsebranch.results == None:
        prune(tree.falsebranch, mingain)
    if tree.truebranch.results == None:
        prune(tree.truebranch, mingain)
    if tree.truebranch.results != None and tree.falsebranch.results != None:
        tb, fb = [], []
        for val, count in tree.truebranch.results.iteritems():
            tb += [[val]] * count
        for val, count in tree.falsebranch.results.iteritems():
            fb += [[val]] * count 
        delta = entropy(tb+fb) - (entropy(tb) + entropy(fb))/2
        if delta < mingain:
            tree.truebranch = None
            tree.falsebranch = None
            tree.results = uniqueCounts(tb+fb)

def missingDataClassify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        if v == None:
            tr = missingDataClassify(observation, tree.truebranch)
            fr = missingDataClassify(observation, tree.falsebranch)
            tc = sum(tr.values())
            fc = sum(fr.values())
            tw = 1.0 * tc / (tc + fc)
            fw = 1.0 * fc / (tc + fc)
            res = {}
            for k, val in tr.iteritems():
                res[k] = val * tw
            for k, val in fr.iteritems():
                if k not in res: res[k] = 0
                res[k] += val * fw
            return res
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v > tree.value: branch = tree.truebranch
            else: branch = tree.falsebranch
        else:
            if v == tree.value: branch = tree.truebranch
            else: branch = tree.falsebranch
        return missingDataClassify(observation, branch)


if __name__ == '__main__':
    tree = buildtree(my_data)
    prune(tree, 1.0)
    print missingDataClassify(['google', None, 'yes', None], tree)
    print missingDataClassify(['google', 'France', None, None], tree)










