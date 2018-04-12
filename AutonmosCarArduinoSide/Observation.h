#ifndef OBSERVATION_H
#define OBSERVATION_H

#define toDigit(c) (c-'0')

#include "Arduino.h"
class Observation {
	private:
		int _echo;
    int _trig;
	public:
		Observation(int trig, int echo);
		int getDistance();
    int getAction();
		void sendToPC(int d);
};
#endif

