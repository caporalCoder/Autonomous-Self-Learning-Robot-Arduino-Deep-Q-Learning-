#include "Observation.h"
#include "Moteur.h"
#include "SoftwareSerial.h"
#include <stdlib.h>
#define BUFFER_SIZE 64//This will prevent buffer overruns.

SoftwareSerial serial_connection(2, 3); //Create a serial connection with TX and RX on these pins

char inData[BUFFER_SIZE]; //This is a character buffer where the data sent by the python script will go.
char inChar=-1; //Initialie the first character as nothing
int count=0; //This is the number of lines sent in from the python script
int i=0; //Arduinos are not the most capable chips in the world so I just create the looping variable once

int Echo_right = A4;  
int Trig_right = A5; 
int Echo_middle = A0;  
int Trig_middle = A1; 
int Echo_left = A2;  
int Trig_left = A3; 
int in1 = 6;
int in2 = 7;
int in3 = 8;
int in4 = 9;
int ENA = 5;
int ENB = 11;
int ABS =100;

Observation observation_R( Echo_right,Trig_right);
Observation observation_M( Echo_middle,Trig_middle);
Observation observation_L( Echo_left,Trig_left);
Moteur moteur(ENA, ENB, ABS, in1, in2, in3, in4);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(Echo_right, INPUT);    
  pinMode(Trig_right, OUTPUT); 
  pinMode(Echo_middle, INPUT);    
  pinMode(Trig_middle, OUTPUT);
  pinMode(Echo_left, INPUT);    
  pinMode(Trig_left, OUTPUT); 
  pinMode(in1,OUTPUT);
  pinMode(in2,OUTPUT);
  pinMode(in3,OUTPUT);
  pinMode(in4,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);

  serial_connection.begin(9600); //Initialize communications with the bluetooth module
  //serial_connection.println("Ready!!!"); //Send something to just start comms. This will never be seen.
  Serial.println("Started"); //Tell the serial monitor that the sketch has started.
  
}

void loop() {
  // put your main code here, to run repeatedly:

  //moteur.applyAction(1); 
  int distance_R = 0;
  int distance_M = 0;
  int distance_L = 0;
  int n = 4;
  for(int i = 0; i< n;i++)
  {
     distance_R += observation_R.getDistance();
     distance_M += observation_M.getDistance();
     distance_L += observation_L.getDistance();
  }
  distance_R /= n;
  distance_M /= n;
  distance_L /= n;

  distance_R = abs(distance_R);
  distance_M = abs(distance_M);
  distance_L = abs(distance_L);
  
  //Serial.println(distance_L);
  
  serial_connection.println(String(distance_L)+","+String(distance_M)+","+String(distance_R));
   byte byte_count=serial_connection.available(); //This gets the number of bytes that were sent by the python script
  do
  {
      byte_count = serial_connection.available();
      
  }while(byte_count == 0);
  
  int first_bytes=byte_count; //initialize the number of bytes that we might handle. 
  int remaining_bytes=0; //Initialize the bytes that we may have to burn off to prevent a buffer overrun
    
  if(first_bytes>=BUFFER_SIZE-1) {
      remaining_bytes=byte_count-(BUFFER_SIZE-1); //Reduce the bytes that we plan on handleing to below the buffer size
  }
    
  for(i=0;i<first_bytes;i++) {
      inChar=serial_connection.read();//Read one byte
      inData[i]=inChar;//Put it into a character string(array)
  }
    
  inData[i]='\0';

   

    
  int act = -1;
  if (String(inData)=="F") {
      count++;                                                                                                                                                                                                                                                                                                                                                                                          
       act = 0;
  } else if (String(inData)=="L") {
      act = 1;
      count++;
  } else if (String(inData) == "R") {
      act = 2;
      count++;
  } else if(String(inData) == "A") {
      act = 4;
      count++;
  }  else {
      Serial.println(inData);
  }
  for(i=0;i<remaining_bytes;i++) {
      inChar=serial_connection.read();
  }

  //Serial.println(count);

  //Serial.println(observation.getDistance());
      // 4 - Apply action
  moteur.applyAction(act); 
    // delay(100); 

        // 1- Get observation
 // int d = observation.getDistance();


  // 2- send observation to pc
 // observation.sendToPC(d);
  //delay(100);
  
  //moteur.applyAction(0); 
}

