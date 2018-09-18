import numpy as np
n = 4
print n
matrix = np.full((n, n), 1)
for i in range(n):
  matrix[i,i] = 0
print matrix
(x, y) = 1 , 2
abc = 0
class game:
  def __init__(self, xmin, ymin, xmax, ymax):
    self.xmin = xmin
    self.ymin = ymin
    self.xmaxnorm = xmax-xmin
    self.ymaxnorm = ymax-ymin
    self.n = (xmax-xmin+1)*(ymax-ymin+1)
    self.matrix = np.full((self.n, self.n), np.inf, dtype=float)
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
    neighs = self.neighbours(obs)
    n = self.from_xy_to_n(obs)
    for x in neighs:
      n1 = self.from_xy_to_n(x)
      self.matrix[n, n1] = np.inf
      self.matrix[n1, n] = np.inf

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

a = game(0,0,40,40)
a.add_obs([1,1])
print a.matrix
