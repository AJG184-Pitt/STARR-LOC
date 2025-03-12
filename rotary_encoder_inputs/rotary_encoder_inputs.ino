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
boolean direction;

Stepper stepper(2048, 4, 6, 5, 7);

void setup() {
  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, INPUT_PULLUP);

  stepper.setSpeed(10);

  Serial.begin(9600);
}

void loop() {
  static int pinALast = digitalRead(pinA);
  
  // Read current state of A and B pins
  int aVal = digitalRead(pinA);
  int bVal = digitalRead(pinB);

  if (aVal != pinALast) { // Check for transitions on A
    if (bVal == aVal) {
      direction = true;   // Clockwise rotation detected
      stepper.step(57);     // Take one step in the correct direction
    } else {
      direction = false;  // Counter-clockwise rotation detected
      stepper.step(-57);   // Take one step in the opposite direction
    }
    
    pinALast = aVal;
  
    Serial.print("Rotated: ");
    if (direction) {
      Serial.println("clockwise");
    } else {
      Serial.println("counterclockwise");
    }

    encoderPosCount += direction ? 1 : -1; // Update position counter based on direction
    Serial.print("Encoder Position: ");
    Serial.println(encoderPosCount);
  }
}
