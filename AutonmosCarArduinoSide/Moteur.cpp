#include "Moteur.h"
#include "Servo.h"
Moteur::Moteur(int _ena,int _enb, int _abs , int pin1, int pin2, int pin3, int pin4){
	_pin1 = pin1;
	_pin2 = pin2;
	_pin3 = pin3;
	_pin4 = pin4;
   ENA = _ena;
   ENB = _enb;
   ABS = _abs;
}
void Moteur::applyAction(int action){
    switch (action) {
      case 0: forward(); break;
      case 1: turnLeft(); break;
      case 2: turnRight(); break;
      case 3: backward(); break;
      case 4: moteurStop(); break;
    }
}

void Moteur::turnLeft(){
	analogWrite(ENA,ABS+10);
 analogWrite(ENB,ABS+10);
  digitalWrite(_pin1,HIGH);
  digitalWrite(_pin2,LOW);
  digitalWrite(_pin3,HIGH);
  digitalWrite(_pin4,LOW); 
  delay(200);
}

void Moteur::turnRight(){
 analogWrite(ENA,ABS+10);
 analogWrite(ENB,ABS+10);
  digitalWrite(_pin1,LOW);
  digitalWrite(_pin2,HIGH);
  digitalWrite(_pin3,LOW);
  digitalWrite(_pin4,HIGH);

  delay(200);
}

void Moteur::forward(){
analogWrite(ENA,ABS*0.8);
 analogWrite(ENB,ABS*0.8);
  digitalWrite(_pin1,HIGH);//digital output
  digitalWrite(_pin2,LOW);
  digitalWrite(_pin3,LOW);
  digitalWrite(_pin4,HIGH);
}

void Moteur::backward(){
 analogWrite(ENA,ABS);
 analogWrite(ENB,ABS);
  digitalWrite(_pin1,LOW);
  digitalWrite(_pin2,HIGH);
  digitalWrite(_pin3,HIGH);
  digitalWrite(_pin4,LOW);
}
void Moteur::moteurStop(){
  analogWrite(ENA,0);
  analogWrite(ENB,0);
  digitalWrite(_pin1,LOW);
  digitalWrite(_pin2,LOW);
  digitalWrite(_pin3,LOW);
  digitalWrite(_pin4,LOW);
}
/*void turnLeft2(int _abs, int _delay)
{
  analogWrite(ENA,_abs);
  analogWrite(ENB,_abs);
  digitalWrite(_pin1,HIGH);
  digitalWrite(_pin2,LOW);
  digitalWrite(_pin3,HIGH);
  digitalWrite(_pin4,LOW); 
  delay(_delay);
}
void turnRight2(int _abs, int _delay)
{
  analogWrite(ENA,_abs);
  analogWrite(ENB,_abs);
  digitalWrite(_pin1,LOW);
  digitalWrite(_pin2,HIGH);
  digitalWrite(_pin3,LOW);
  digitalWrite(_pin4,HIGH);
  delay(_delay);
}
*/
