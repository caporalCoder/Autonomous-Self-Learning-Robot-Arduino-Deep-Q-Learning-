#include "Observation.h"
Observation::Observation(int echo, int trig){
	_echo = echo;
  _trig = trig;
}

int Observation::getDistance() {
	digitalWrite(_trig, LOW);   
  delayMicroseconds(2);
  digitalWrite(_trig, HIGH);  
  delayMicroseconds(20);
  digitalWrite(_trig, LOW);   
  float Fdistance = pulseIn(_echo, HIGH);  
  Fdistance= Fdistance/58;       
  return (int)Fdistance;
}

void Observation::sendToPC(int d) {

}

int Observation::getAction() {
  return toDigit(Serial.read());
}


