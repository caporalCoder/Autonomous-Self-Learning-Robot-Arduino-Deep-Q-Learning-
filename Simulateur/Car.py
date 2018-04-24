
import numpy as np
import math
import random
import matplotlib.pyplot as plt


class Car(object):
    def __init__(self,lag, ang):
        self.lag=lag
        self.ang=ang
        self.pos0 = np.array([0, 0])
        self.capM = np.array([0, lag])
        self.capL = self.pos0 + self.lag*np.array([math.cos((90+self.ang)*math.pi/180), math.sin((90+self.ang)*math.pi/180)])
        self.capR = self.pos0 + self.lag*np.array([math.cos((90-self.ang)*math.pi/180), math.sin((90-self.ang)*math.pi/180)])
        self.speed = 0.0

    # Afficher
    def show(self):
        body = np.array([self.capL,self.pos0,self.capM,self.pos0,self.capR,self.pos0])
        plt.plot(body[:,0], body[:,1], 'k')
        plt.plot(self.pos0[0],self.pos0[1],'ro')
        plt.plot(self.capM[0],self.capM[1], 'bo', ms=3)
        plt.plot(self.capL[0],self.capL[1], 'go', ms=3)
        plt.plot(self.capR[0],self.capR[1], 'mo', ms=3)

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
        Dx = self.capM[0] - self.pos0[0]
        Dy = self.capM[1] - self.pos0[1]

        dx = distance*(Dx/self.lag)
        dy = distance*(Dy/self.lag)

        self.pos0 = self.pos0 + np.array([dx, dy])
        self.capM = self.capM  + np.array([dx, dy])
        self.capL = self.capL  + np.array([dx, dy])
        self.capR = self.capR  + np.array([dx, dy])

    # Tourner
    def rotation(self,direction,delta_t):
        ang_speed = 0.1*20.0*self.speed*math.pi
        dtheta = ang_speed*delta_t
        if direction==1: # Si c'est a DROITE
            dtheta = -dtheta

        self.capM = self.capM  - self.pos0
        self.capR = self.capR  - self.pos0
        self.capL = self.capL  - self.pos0

        rot_mat = np.array([[math.cos(dtheta), -math.sin(dtheta)], [math.sin(dtheta), math.cos(dtheta)]])
        self.capM = np.dot(rot_mat,self.capM) + self.pos0
        self.capR = np.dot(rot_mat,self.capR) + self.pos0
        self.capL = np.dot(rot_mat,self.capL) + self.pos0


    # Lecture d'un capteur unique
    def detect(self,sensor,obstacles):
        x0=self.pos0[0]
        y0=self.pos0[1]
        x1=sensor[0]
        y1=sensor[1]
#        print('cap ',x0,y0,x1,y1)
        # Eq droite capteur
        if abs(x0-x1)<=0.0001:
            a1=1E4*(y1-y0)/abs(y1-y0)
            b1=y1
        else:
            a1 = (y1-y0)/(x1-x0)
            b1 = (y0*x1 - x0*y1)/(x1-x0)

        #Segments des objets
        segm=[]
        for obj in obstacles:
            segm.append([obj.c1, obj.c2])
            segm.append([obj.c2, obj.c3])
            segm.append([obj.c3, obj.c4])
            segm.append([obj.c4, obj.c1])
#        print('segm ', segm)

        #Eq Droites des segments
        eq = []
        for segment in segm:
            xs0=segment[0][0]
            ys0=segment[0][1]
            xs1=segment[1][0]
            ys1=segment[1][1]
            # Eq segment
 #           print('Psegment ',xs0,ys0,xs1,ys1)
            if abs(xs0-xs1)<=0.0001:
                pente=1E5*(ys1-ys0)/abs(ys1-ys0)
                b0=ys0
            else:
                pente = (ys1-ys0)/(xs1-xs0)
                b0 = (ys0*xs1 - xs0*ys1)/(xs1-xs0)
            eq.append([pente, b0])
 #       print('Eq ', eq)

        #Coord de l'intersec
        coord = []
        for droite in eq:
            a2 = droite[0]
            b2 = droite[1]
            x_int = -(b2-b1)/(a2-a1)
            y_int = (-a1*b2 + b1*a2)/(a2-a1)
            coord.append([x_int, y_int])
#        print('coord ', coord)

        #Distances
        dist = []
        for i in range(len(segm)):
            D = obstacles[0].width

            di_c1= math.sqrt( (segm[i][0][0] - coord[i][0])**2 + (segm[i][0][1] - coord[i][1])**2 )
            di_c2= math.sqrt( (segm[i][1][0] - coord[i][0])**2 + (segm[i][1][1] - coord[i][1])**2 )
            dsegm = math.sqrt( (segm[i][0][0] - segm[i][1][0])**2 + (segm[i][0][1] - segm[i][1][1])**2 )
#            print('di_c1, di_c2, dsegm', di_c1, di_c2, dsegm )

            if di_c1 + di_c2 <= dsegm+0.001:

                intersect = np.array(coord[i]) - self.pos0
                mid = sensor - self.pos0
                if mid[0]*intersect[0]>=0 and mid[1]*intersect[1]>=0:
                    D = math.sqrt( (sensor[0] - coord[i][0])**2 + (sensor[1] - coord[i][1])**2 )

            dist.append(D)


        #Trouer le minimum et donner la lecture
        index = np.argmin(dist)
        return [coord[index], dist[index]]


    # Lecture de la voiture (3 capteurs)
    def read(self,obstacles):
        lecL = self.detect(self.capL,obstacles)
        lecM = self.detect(self.capM,obstacles)
        lecR = self.detect(self.capR,obstacles)

        # Retourner
        lecture = [lecL[1], lecM[1], lecR[1]]
        points = [lecL[0], lecM[0], lecR[0]]
#        print('lecture ', lecture)
#        print('points ', points)
        return [lecture, points]
