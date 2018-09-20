#!/usr/bin/env python
import rospy
import serial
import random
from pacman.msg import actions
from pacman.msg import pacmanPos
from pacman.msg import ghostsPos
from pacman.msg import cookiesPos
from pacman.msg import bonusPos
from pacman.msg import game
from pacman.msg import performance
from pacman.srv import mapService
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
    pass

def ghostsPosCallback(msg):
    #rospy.loginfo('# Ghosts: {} '.format(msg.nGhosts)) 
    #for i in range(msg.nGhosts):
    #    rospy.loginfo('Pos Ghosts {}: PosX {} PosY {}'.format(i, msg.ghostsPos[i].x, msg.ghostsPos[i].y))
    pass

def cookiesPosCallback(msg):
    #rospy.loginfo('# Cookies: {} '.format(msg.nCookies)) 
    #for i in range(msg.nCookies):
    #    rospy.loginfo('Pos Cookies {}: PosX {} PosY {}'.format(i, msg.cookiesPos[i].x, msg.cookiesPos[i].y))
    pass

def bonusPosCallback(msg):
    #rospy.loginfo('# bonus: {} '.format(msg.nBonus)) 
    #for i in range(msg.nBonus):
    #    rospy.loginfo('Pos Bonus {}: PosX {} PosY {}'.format(i, msg.bonusPos[i].x, msg.bonusPos[i].y))
    pass

def gameStateCallback(msg):
    #mensaje = 'Game State: {} '.format(msg.state)
    #rospy.loginfo(mensaje) 
    #ser.write(mensaje)
    pass

def performanceCallback(msg):
    #mensaje = 'Lives: {} Score: {} Time: {} PerformEval: {}'.format(msg.lives, msg.score, msg.gtime, msg.performEval)
    mensajeArduino = 'Lives: {} Score: {} Time: {}'.format(msg.lives, msg.score, msg.gtime)
    #rospy.loginfo(mensajeArduino)

def pacman_controller_py_sol():

    rospy.init_node('pacman_controller_py_sol', anonymous=True)
    pub = rospy.Publisher('pacmanActions0', actions, queue_size=50)
    rospy.Subscriber('pacmanCoord0', pacmanPos, pacmanPosCallback)
    rospy.Subscriber('ghostsCoord', ghostsPos, ghostsPosCallback)
    rospy.Subscriber('cookiesCoord', cookiesPos, cookiesPosCallback)
    rospy.Subscriber('bonusCoord', bonusPos, bonusPosCallback)
    rospy.Subscriber('gameState', game, gameStateCallback)
    rospy.Subscriber('performanceEval', performance, performanceCallback)
    
    try:
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("Controlador Remoto")
        rospy.loginfo("# Obs: {}".format(mapa.nObs))
        rospy.loginfo("minX : {}  maxX : {}".format(mapa.minX, mapa.maxX))
        rospy.loginfo("minY : {}  maxY : {}".format(mapa.minY, mapa.maxY))
        
        rate = rospy.Rate(50) # 10hz
        msg = actions();
        msg.action = 0
        joysitckY = 511
        joysitckX = 511
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
        
    except rospy.ServiceException as e:
        print ("Error!! Make sure pacman_world node is running ")
    
if __name__ == '__main__':
    try:
        pacman_controller_py_sol()
    except rospy.ROSInterruptException:
        pass
