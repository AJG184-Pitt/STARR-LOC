#include <Stepper.h>

/*==========================================================================
// Author : Handson Technology
// Project : Arduino Uno with KY040 Rotary Encoder Module
// Description : Reading rotary encoder Value with Arduino Uno
// Source-Code : KY040_Rotary.ino
// Module: KY040
//==========================================================================
*/
int pinA = 2; // Connected to CLK on KY-040
int pinB = 3; // Connected to DT on KY-040
int encoderPosCount = 0;
int pinALast;
int aVal;
boolean bCW;

// Need to multiply steps by 64 due to the gear ratio
Stepper stepper(32, 8,9,10,11);

void setup() {
  pinMode (pinA, INPUT_PULLUP);
  pinMode (pinB, INPUT_PULLUP);
  stepper.setSpeed(200);
  /* Read Pin A
  Whatever state it's in will reflect the last position
  */
  pinALast = digitalRead(pinA);
  Serial.begin (9600);
}

void loop() {
  aVal = digitalRead(pinA);
  // int val = 0
  if (aVal != pinALast) { // Means the knob is rotating
    // if the knob is rotating, we need to determine direction
    // We do that by reading pin B.
    if (digitalRead(pinB) != aVal) { // Means pin A Changed first - We're Rotating Clockwise.
      encoderPosCount++;
      bCW = true;
      stepper.step(3.2*64);
    } else {// Otherwise B changed first and we're moving CCW
      bCW = false;
      encoderPosCount--;
      stepper.step(-3.2*64);
    }
    
    Serial.print ("Rotated: ");
    if (bCW){
      Serial.println ("clockwise");
    }else{
      Serial.println("counterclockwise");
    }
  
    Serial.print("Encoder Position: ");
    Serial.println(encoderPosCount);
  }
  
  pinALast = aVal;
}
