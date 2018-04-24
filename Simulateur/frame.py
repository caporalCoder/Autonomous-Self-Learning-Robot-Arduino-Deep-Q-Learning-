
import numpy as np
import math
import random
import matplotlib.pyplot as plt


class frame(object):
    def __init__(self, center, angle, w, h):
        self.center = np.array(center)
        self.width = w
        self.height = h
        self.c1 = np.array([-w/2, -h/2])
        self.c2 = np.array([-w/2, +h/2])
        self.c3 = np.array([w/2, +h/2])
        self.c4 = np.array([w/2, -h/2])
        self.cap = np.array([0, h/2])
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        self.cap = np.dot(rot_mat,self.cap) + self.center
        self.c1 = np.dot(rot_mat,self.c1) + self.center
        self.c2 = np.dot(rot_mat,self.c2) + self.center
        self.c3 = np.dot(rot_mat,self.c3) + self.center
        self.c4 = np.dot(rot_mat,self.c4) + self.center
        self.speed = 0

    def show(self):
        total=np.array([self.c1,self.c2,self.c3,self.c4,self.c1])
        plt.plot(total[:,0],total[:,1])

    # Bouger selon une action choisie
    def move(self,type,delta_t):
        if type==0: #Avancer
            self.advance(delta_t)
        elif type==1: #Gauche
            self.rotation(0,delta_t)
            self.advance(delta_t)
        elif type==2: #Droite
            self.rotation(1,delta_t)
            self.advance(delta_t)
        elif type==3: #Arret
            self.speed = self.speed
        elif type==4: #Shutdown
            self.speed = 0.0
        elif type==5: #Accelerer
            self.speed = 1.01*self.speed
        elif type==6: #Decelerer
            self.speed = 0.99*self.speed

    # Avancer
    def advance(self,delta_t):
        distance = self.speed*delta_t
        Dx = self.cap[0] - self.center[0]
        Dy = self.cap[1] - self.center[1]

        dx = distance*(Dx/self.lag)
        dy = distance*(Dy/self.lag)

        self.center = self.center + np.array([dx, dy])
        self.cap = self.cap + np.array([dx, dy])
        self.c1 = self.c1  + np.array([dx, dy])
        self.c2 = self.c2  + np.array([dx, dy])
        self.c3 = self.c3  + np.array([dx, dy])
        self.c4 = self.c4  + np.array([dx, dy])

    # Tourner
    def rotation(self,direction,delta_t):
        ang_speed = 0.1*20.0*self.speed*math.pi
        dtheta = ang_speed*delta_t
        if direction==1: # Si c'est a DROITE
            dtheta = -dtheta

        self.cap = self.cap  - self.center
        self.c1 = self.c1  - self.center
        self.c2 = self.c2  - self.center
        self.c3 = self.c3  - self.center
        self.c4 = self.c4  - self.center

        rot_mat = np.array([[math.cos(dtheta), -math.sin(dtheta)], [math.sin(dtheta), math.cos(dtheta)]])
        self.cap = np.dot(rot_mat,self.cap) + self.center
        self.c1 = np.dot(rot_mat,self.c1) + self.center
        self.c2 = np.dot(rot_mat,self.c2) + self.center
        self.c3 = np.dot(rot_mat,self.c3) + self.center
        self.c4 = np.dot(rot_mat,self.c4) + self.center
