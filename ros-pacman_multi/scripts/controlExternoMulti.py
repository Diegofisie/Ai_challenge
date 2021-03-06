#!/usr/bin/env python
import random
import rospy
import serial
import threading
import numpy as np
from pacman.msg import actions
from pacman.msg import pacmanPos
from pacman.msg import ghostsPos
from pacman.msg import cookiesPos
from pacman.msg import bonusPos
from pacman.msg import game
from pacman.msg import performance
from pacman.srv import mapService

posx = 0
posy = 0
ghosts = []
mode = []
cookies = []
pills = []

ser = ""
try:
    ser = serial.Serial('/dev/ttyACM0',9600,timeout=2)
except :
    try:
        ser = serial.Serial('/dev/ttyACM1',9600,timeout=2)
    except:
        try:
            ser = serial.Serial('/dev/ttyACM2',9600,timeout=2)
        except rospy.ServiceException as e:
            print ("Error!! Make sure arduino is connected to a port")
mensajeArduino = "";

def pacmanPosCallback(msg):
    #rospy.loginfo('# Pacmans: {} posX: {} PosY: {}'.format(msg.nPacman, msg.pacmanPos.x, msg.pacmanPos.y) )
    global posx
    global posy
    posx = msg.pacmanPos.x
    posy = msg.pacmanPos.y

def ghostsPosCallback(msg):
    #rospy.loginfo('# Ghosts: {} '.format(msg.nGhosts)) 
    #for i in range(msg.nGhosts):
       #rospy.loginfo('Pos Ghosts {}: PosX {} PosY {}'.format(i, msg.ghostsPos[i].x, msg.ghostsPos[i].y))
    global ghosts
    global mode
    ghosts = msg.ghostsPos
    mode = msg.mode

def cookiesPosCallback(msg):
    #rospy.loginfo('# Cookies: {} '.format(msg.nCookies)) 
    #for i in range(msg.nCookies):
        #rospy.loginfo('Pos Cookies {}: PosX {} PosY {}'.format(i, msg.cookiesPos[i].x, msg.cookiesPos[i].y))
    global cookies
    cookies = msg.cookiesPos

def bonusPosCallback(msg):
    #rospy.loginfo('# bonus: {} '.format(msg.nBonus)) 
    #for i in range(msg.nBonus):
        #rospy.loginfo('Pos Bonus {}: PosX {} PosY {}'.format(i, msg.bonusPos[i].x, msg.bonusPos[i].y))
    global pills
    pills = msg.bonusPos

def gameStateCallback(msg):
    #rospy.loginfo('Game State: {} '.format(msg.state)) 
    pass

def performanceCallback(msg):
    #rospy.loginfo('Lives: {} Score: {} Time: {} PerformEval: {}'.format(msg.lives, msg.score, msg.gtime, msg.performEval) )
    mensajeArduino = 'Lives: {} Score: {} Time: {}'.format(msg.lives, msg.score, msg.gtime)
    


class game2:
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
        self.mapn = np.full(self.n, 0)
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
        obs[0] = obs[0]-self.xmin
        obs[1] = obs[1]-self.ymin
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
        x = a[0]
        y = a[1]
        neighs = np.zeros((0,2), dtype=float)
        movsx = np.array([-1,1,0,0])
        movsy = np.array([0,0,-1,1])
        for i in range(4):
            x1 = x+movsx[i]
            y1 = y+movsy[i]
            if x1 < 0 or x1 > self.xmaxnorm or y1 < 0 or y1 > self.ymaxnorm or self.is_obs[self.from_xy_to_n([x1,y1])]:
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

    def init_mapn(self):
        index = 0
        for i in range(self.n):
            if not self.is_obs[i]:
                self.mapn[i] = index
                index = index+1

    def from_xy_to_n2(self, arr):
        n = self.from_xy_to_n(arr)
        return self.mapn[n]
    
    def evaluate(self, pacman, cookies, pills, phantoms, mode):
        pos = self.from_xy_to_n2([pacman[0], pacman[1]])
        evalu = 0.0
        for ck in cookies:
            posck = self.from_xy_to_n2([ck.x-self.xmin, ck.y-self.ymin])
            dist = self.matrix_no_obs[pos, posck]
            evalu = evalu + 5/(dist+1.0)
        nearest_ph = np.inf
        for i in range(len(phantoms)):
            posph = self.from_xy_to_n2([phantoms[i].x-self.xmin, phantoms[i].y-self.ymin])
            dist = self.matrix_no_obs[pos, posph]
            if not mode[i]:
                evalu = evalu - 15/(dist)
                if dist < nearest_ph: nearest_ph = dist
            else:
                evalu = evalu + 20/(dist+1.0)
        for p in pills:
            posp = self.from_xy_to_n2([p.x-self.xmin, p.y-self.ymin])
            dist = self.matrix_no_obs[pos, posp]
            evalu = evalu + 2/(dist+1.0) + 8/nearest_ph
        return evalu

def eval_mov(fromD, to):
    return int((1+fromD[1]-to[1])/2) + int((1+fromD[0]-to[0])/2+2)*abs(fromD[0]-to[0])

def pacman1(msg,pub,rate,mapa):
    g = game2(mapa.minX, mapa.minY, mapa.maxX, mapa.maxY, mapa.nObs)
    for o in mapa.obs:
        x = o.x
        y = o.y
        g.add_obs([x,y])
    g.init_matrix()
    g.init_mapn()
    g.floyd_warshall()
    while not rospy.is_shutdown():
            neighs = g.neighbours([posx-g.xmin, posy-g.ymin])
            optimalindex = 0
            optimal = -np.inf
            for i in range(len(neighs)):
                eval = g.evaluate(neighs[i], cookies, pills, ghosts, mode)
                if eval > optimal:
                    optimal = eval
                    optimalindex = i
            msg.action = eval_mov([posx-g.xmin, posy-g.ymin], neighs[optimalindex]);
            pub.publish(msg.action)
            rate.sleep()

def pacman2(msg,pub,rate):
    msg.action = 0
    joysitckY = 337
    joysitckX = 337
    rospy.loginfo("Entro")
    while not rospy.is_shutdown():
            leyo = False
            while not leyo:
                try:
                    posicionJoystick = ser.readline()
                    joysitckY=int((posicionJoystick.split(","))[0])
                    joysitckX=int((posicionJoystick.split(","))[1])
                   
                    if (joysitckY > 660):
                        msg.action = 2
                    elif(joysitckY < 50):
                        msg.action = 3

                    if (joysitckX > 669):
                        msg.action = 0
                    elif(joysitckX < 50):
                        msg.action = 1
                    leyo = True
                except:
                    pass
                ser.flushInput()
                ser.write(mensajeArduino)
                pub.publish(msg.action)
                rate.sleep()

def pacman_controller_py_sol():
    global posx
    global posy
    global ghosts
    global mode
    global cookies
    global pills
    rospy.init_node('pacman_controller_py_sol', anonymous=True)
    pub1 = rospy.Publisher('pacmanActions0', actions, queue_size=10)
    pub2 = rospy.Publisher('pacmanActions1', actions, queue_size=50)
    rospy.Subscriber('pacmanCoord0', pacmanPos, pacmanPosCallback)
    rospy.Subscriber('ghostsCoord', ghostsPos, ghostsPosCallback)
    rospy.Subscriber('cookiesCoord', cookiesPos, cookiesPosCallback)
    rospy.Subscriber('bonusCoord', bonusPos, bonusPosCallback)
    rospy.Subscriber('gameState', game, gameStateCallback)
    rospy.Subscriber('performanceEval', performance, performanceCallback)
    
    try:
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("Controlador AI")
        rospy.loginfo("# Obs: {}".format(mapa.nObs))
        rospy.loginfo("minX : {}  maxX : {}".format(mapa.minX, mapa.maxX))
        rospy.loginfo("minY : {}  maxY : {}".format(mapa.minY, mapa.maxY))

        msg = actions()
                
        rate = rospy.Rate(50) # 10hz
        threading.Thread(target=pacman2,args=(msg,pub2,rate)).start()
        threading.Thread(target=pacman1,args=(msg,pub1,rate,mapa)).start()
        
        
    except rospy.ServiceException as e:
        print ("Error!! Make sure pacman_world node is running ")
    
if __name__ == '__main__':
    try:
        pacman_controller_py_sol()
    except rospy.ROSInterruptException:
        pass

