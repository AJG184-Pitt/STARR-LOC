#include <Stepper.h>

/*==========================================================================
// Description : Combined code for rotary encoder and slider control
//==========================================================================
*/

// Rotary Encoder pins
int pinA = 2;   // Connected to CLK on KY-040
int pinB = 3;   // Connected to DT on KY-040
int encoderPosCount = 0;
boolean direction;

// Slider pin 
const int sliderPin = A0;  // Connected to analog pin

// Direction and step pins for stepper2 (direct control)
const int dirPin = 8;
const int stepPin = 9;

// 28BYJ-48 Stepper configuration
const int stepsPerRevolution = 32; // Internal steps per revolution
const int gearRatio = 64; // Internal gear ratio for 28BYJ-48
const float stepsPerDegree = (stepsPerRevolution * gearRatio) / 360.0; // ~5.69 steps per degree

// User settings - ADJUST THESE FOR DIFFERENT ROTATION AMOUNTS
const float degreesPerStep = 1.0; // Set how many degrees to move per slider step
const int sliderRange = 100; // Number of positions on the slider (0 to sliderRange)
const int minStepThreshold = 1; // Minimum steps to move

// Position tracking
int currentPosition = 0;

// Timing variables for step pulse generation - CRITICAL for proper movement
const int stepPulseWidth = 1000;  // Pulse width in microseconds
const int stepPulseDelay = 1500;  // Microseconds between pulses

// Stepper motor for rotary encoder
Stepper stepper(2048, 4, 6, 5, 7);

void setup() {
  // Rotary encoder setup
  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, INPUT_PULLUP);
  
  // Slider setup
  pinMode(sliderPin, INPUT);
  
  // Stepper motor driver setup
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  digitalWrite(stepPin, LOW);
  
  // Set stepper speed
  stepper.setSpeed(10);
  
  Serial.begin(9600);
  Serial.println("Initialized combined control system");
}

void loop() {
  // ===== ROTARY ENCODER HANDLING =====
  static int pinALast = digitalRead(pinA);
  
  // Read current state of A and B pins
  int aVal = digitalRead(pinA);
  int bVal = digitalRead(pinB);

  if (aVal != pinALast) { // Check for transitions on A
    if (bVal == aVal) {
      direction = true;   // Clockwise rotation detected
      stepper.step(57);   // Take steps in the correct direction - simple approach
    } else {
      direction = false;  // Counter-clockwise rotation detected
      stepper.step(-57);  // Take steps in the opposite direction - simple approach
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

  // ===== SLIDER HANDLING =====
  // Read the current slider value
  int sliderValue = analogRead(sliderPin);
  
  // Map slider value to a target position (0 to sliderRange)
  int targetPosition = map(sliderValue, 0, 1023, 0, sliderRange);
  
  // Calculate steps to move
  int stepsToMove = targetPosition - currentPosition;
  
  // Only move if the change exceeds the threshold
  if (abs(stepsToMove) >= minStepThreshold) {
    // Set direction based on movement direction
    if (stepsToMove > 0) {
      digitalWrite(dirPin, HIGH); // Clockwise
    } else {
      digitalWrite(dirPin, LOW); // Counter-clockwise
    }
    
    // Calculate degrees to move
    float degreesToMove = abs(stepsToMove) * degreesPerStep;
    
    // Convert degrees to motor steps
    int totalSteps = round(degreesToMove * stepsPerDegree);
    
    // Take steps with careful timing
    for (int i = 0; i < totalSteps; i++) {
      // Generate one step pulse with longer HIGH time
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(stepPulseWidth);
      digitalWrite(stepPin, LOW);
      
      // Delay between pulses to ensure motor can keep up
      delayMicroseconds(stepPulseDelay);
    }
    
    // Update current position
    currentPosition = targetPosition;
    
    // Print for debugging
    Serial.print("Target: ");
    Serial.print(targetPosition);
    Serial.print(" | Current: ");
    Serial.print(currentPosition);
    Serial.print(" | Degrees: ");
    Serial.print(degreesToMove);
    Serial.print(" | Steps: ");
    Serial.println(totalSteps);
  }
  
  // Small delay for overall timing - balance between responsiveness and stability
  delay(10);  // Reduced delay for better responsiveness
}
