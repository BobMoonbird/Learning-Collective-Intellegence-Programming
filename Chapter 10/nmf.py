import numpy as np, random
np.seterr(divide='ignore', invalid='ignore')

def diffcost(matrix1, matrix2):
	dif = 0
	for i in range(np.shape(matrix1)[0]):
		for j in range(np.shape(matrix1)[1]):
			dif += pow(matrix1[i, j] - matrix2[i, j], 2)
	return dif

def factorize(matrix, k=10, maxIterations=50):
	m = np.shape(matrix)[0]
	n = np.shape(matrix)[1]
	w = np.matrix([[random.random() for j in range(k)] for i in range(m)])
	h = np.matrix([[random.random() for j in range(n)] for i in range(k)])
	for i in range(maxIterations):
		wh = w * h
		cost = diffcost(matrix, wh)
		if cost == 0: break
		hn = w.T * matrix
		hd = w.T * w * h
		h = np.matrix(np.array(h)*np.array(hn)/np.array(hd))
		h[np.isnan(h)] = 0
		wn = matrix * h.T
		wd = w * h * h.T
		w = np.matrix(np.array(w)*np.array(wn)/np.array(wd))
		w[np.isnan(w)] = 0
	return w, h

if __name__ == '__main__':
	m1 = np.matrix([[1, 2, 3], [4, 5, 6]])
	m2 = np.matrix([[1, 2], [3, 4], [5, 6]])
	w, h = factorize(m1 * m2, k=2, maxIterations=100)
	print w
	print h
	print w * h
	print m1 * m2