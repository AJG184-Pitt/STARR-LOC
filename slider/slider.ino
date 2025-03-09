#include <Stepper.h>

const int sliderPin = A0;
const int stepperStepsPerRevolution = 32;
const int minStepThreshold = 5; // Minimum steps to move

Stepper stepper(stepperStepsPerRevolution, 4, 6, 5, 7);

int currentPosition = 0;

void setup() {
  pinMode(sliderPin, INPUT);
  stepper.setSpeed(200);
  Serial.begin(9600);
}

void loop() {
  int sliderValue = analogRead(sliderPin);
  Serial.println(sliderValue);

  int targetPosition = map(sliderValue, 0, 1023, 0, stepperStepsPerRevolution);
  
  int stepsToMove = targetPosition - currentPosition;
  
  if (abs(stepsToMove) > minStepThreshold) {        
    stepper.step(stepsToMove * 64);
    currentPosition += stepsToMove;
  }
}
