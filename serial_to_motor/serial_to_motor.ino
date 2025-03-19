#include <Stepper.h>

// Motor 1 (X-axis) uses Stepper library
const int STEPPER_STEPS = 32;
const int GEAR_RATIO = 64;

// Motor 2 (Y-axis) uses direct control pins
const int dirPin = 8;
const int stepPin = 9;

// User settings
const float degreesPerStep = 10.0; // Same for both motors

// Timing variables for direct pulse generation
const int stepPulseWidth = 1000;  // Pulse width in microseconds
const int stepPulseDelay = 1500;  // Microseconds between pulses

// Setup stepper motor with Stepper library
// Stepper stepper1(STEPPER_STEPS, 4, 6, 5, 7);

void setup() {
  // Setup for X-axis motor
  // stepper1.setSpeed(200);

  // Setup for Y-axis motor
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  digitalWrite(stepPin, LOW);
  
  Serial.begin(9600);
  Serial.println("Dual motor controller ready. Send 'x y' values.");
}

void loop() {
  // Check if data is available from serial connection
  if (Serial.available() > 0) {
    // Wait a bit for the entire message to arrive
    delay(100);

    // Read the whole string
    String inputString = "";
    while (Serial.available() > 0) {
      char inChar = (char)Serial.read();
      inputString += inChar;
      delay(100);
    }

    // Parse the string for x and y values
    int spaceIndex = inputString.indexOf(' ');
    if (spaceIndex != -1) {
      float x_dir = inputString.substring(0, spaceIndex).toFloat();
      float y_dir = inputString.substring(spaceIndex + 1).toFloat();

      // Echo back what was received
      Serial.print("Received x: ");
      Serial.print(x_dir, 5);
      Serial.print(", y: ");
      Serial.println(y_dir, 5);

      // Handle X motor (using Stepper library)
      // if (deltaX != 0) {
      //   // Convert deltaX to degrees and then to steps
      //   float degreesToMoveX = abs(deltaX) * degreesPerStep;
      //   int stepsToMoveX = round(degreesToMoveX * stepsPerDegree);
        
      //   // Set proper direction
      //   if (deltaX > 0) {
      //     stepper1.step(stepsToMoveX);
      //   } else {
      //     stepper1.step(-stepsToMoveX);
      //   }
        
      //   Serial.print("X moved: ");
      //   Serial.print(degreesToMoveX);
      //   Serial.println(" degrees");
      // }

      // Handle Y motor (using direct control)
      if (y_dir != 0) {
        // Set direction based on movement direction
        if (y_dir > 0) {
          digitalWrite(dirPin, HIGH); // Clockwise
        } else {
          digitalWrite(dirPin, LOW);  // Counter-clockwise
        }

        // Move stepper by step amount
        // int totalSteps = abs(y_dir);

        // Take steps with careful timing
        for (int i = 0; i < abs(y_dir); i++) {
          // Generate one step pulse
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(stepPulseWidth);
          digitalWrite(stepPin, LOW);
          
          // Delay between pulses
          delayMicroseconds(stepPulseDelay);
        }
        
        Serial.print("Y moved: ");
        Serial.print(y_dir);
        Serial.println(" steps");
      }

    } else {
      // Error output for unexpected format
      Serial.println("Error: Expected format 'x y'");
    }
  }
}
