const int sliderPin = A0;
const int dirPin = 8;
const int stepPin = 9;
const int minStepThreshold = 1; // Minimum steps to move

// 28BYJ-48 Stepper configuration
const int stepsPerRevolution = 32; // Internal steps per revolution
const int gearRatio = 64; // Internal gear ratio for 28BYJ-48
const float stepsPerDegree = (stepsPerRevolution * gearRatio) / 360.0; // ~5.69 steps per degree

// User settings - ADJUST THESE FOR DIFFERENT ROTATION AMOUNTS
const float degreesPerStep = 1.0; // Set how many degrees to move per slider step
const int sliderRange = 100; // Number of positions on the slider (0 to sliderRange)

// Position tracking
int currentPosition = 0;

// Timing variables for step pulse generation - CRITICAL for proper movement
const int stepPulseWidth = 1000;  // Pulse width in microseconds
const int stepPulseDelay = 1500;  // Microseconds between pulses

void setup() {
  pinMode(sliderPin, INPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  
  // Initialize step pin to LOW
  digitalWrite(stepPin, LOW);
  
  Serial.begin(9600);
}

void loop() {
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
  
  delay(100); // Delay to allow motor to complete movement
}