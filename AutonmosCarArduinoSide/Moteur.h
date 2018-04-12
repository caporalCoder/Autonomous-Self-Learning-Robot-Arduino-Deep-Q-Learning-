#ifndef MOTEUR_H
#define MOTEUR_H

#include "Arduino.h"
class Moteur{
		private:
      int ENA;
      int ENB;
      int ABS;
			int _pin1;
			int _pin2;
			int _pin3;
			int _pin4;
			void turnLeft();
			void turnRight();
      //void turnLeft2(int _abs, int _delay);
      //void turnRight2(int _abs, int _delay);
			void forward();
			void backward();
      void moteurStop();
		public:
			Moteur (int, int, int,  int pin1, int pin2, int pin3,int pin4);
			void applyAction(int action);						
};
#endif

