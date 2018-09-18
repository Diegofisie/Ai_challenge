import numpy as np
import time
n = 4
print n
matrix = np.full((n, n), 1)
for i in range(n):
  matrix[i,i] = 0
print matrix
(x, y) = 1 , 2
abc = 0
class game:
  def __init__(self, xmin, ymin, xmax, ymax, nobs):
    self.xmin = xmin
    self.ymin = ymin
    self.xmaxnorm = xmax-xmin
    self.ymaxnorm = ymax-ymin
    self.n = (xmax-xmin+1)*(ymax-ymin+1)
    self.n2 = self.n - nobs
    self.matrix = np.full((self.n, self.n), np.inf, dtype=float)
    self.matrix_no_obs = np.full((self.n2, self.n2), np.inf, dtype=float)
    self.is_obs = np.full(self.n, False)
    for i in range(self.n):
      self.matrix[i,i] = 0
    for i in range(self.xmaxnorm+1):
      for j in range(self.ymaxnorm+1):
        neighs = self.neighbours([i,j])
        n = self.from_xy_to_n([i,j])
        for x in neighs:
          n1 = self.from_xy_to_n(x)
          self.matrix[n, n1], self.matrix[n1, n] = 1, 1
  
  def from_xy_to_n(self, arr):
    return int(arr[0])*(self.ymaxnorm+1) + int(arr[1])
  
  def add_obs(self, obs):
    n = self.from_xy_to_n(obs)
    self.is_obs[n] = True
  
  def init_matrix(self):
    indexi = 0
    for i in range(self.n):
      if self.is_obs[i]:
        continue
      indexj = 0
      for j in range(self.n):
        if not self.is_obs[j]:
          self.matrix_no_obs[indexi, indexj] = self.matrix[i,j]
          indexj = indexj+1
      indexi = indexi+1

  def neighbours(self, a):
    x = a[0]-self.xmin
    y = a[1]-self.ymin
    neighs = np.zeros((0,2), dtype=float)
    movsx = np.array([-1,1,0,0])
    movsy = np.array([0,0,-1,1])
    for i in range(4):
      x1 = x+movsx[i]
      y1 = y+movsy[i]
      if x1 < 0 or x1 > self.xmaxnorm or y1 < 0 or y1 > self.ymaxnorm:
        continue
      neighs = np.append(neighs, np.array([[x1, y1]]), axis=0)
    return neighs
  
  def floyd_warshall(self):
    for k in range(self.n2):
      for i in range(self.n2):
        for j in range(self.n2):
          dist = self.matrix_no_obs[i,k]+self.matrix_no_obs[k,j]
          if dist < self.matrix_no_obs[i,j]:
            self.matrix_no_obs[i,j] = dist

init = time.time()
a = game(0,0,3,3,0)
a.init_matrix()
a.floyd_warshall()
print a.matrix_no_obs
print a.matrix
print time.time()-init
