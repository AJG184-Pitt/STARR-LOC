#include <Stepper.h>

int pinA = 2;   // Connected to CLK on KY-040
int pinB = 3;   // Connected to DT on KY-040
int pinC = A0;  // Connected to analog pin

const int STEPPER_STEPS = 32;
const int GEAR_RATIO = 64;

// Need to multiply steps by 64 due to the gear ratio
Stepper stepper1(STEPPER_STEPS, 4, 6, 5, 7);
Stepper stepper2(STEPPER_STEPS, 8, 10, 9, 11);

void setup() {
  stepper1.setSpeed(200);
  stepper2.setSpeed(200);  
  Serial.begin(9600);
}

void loop() {
  // Check if data is available from serial connection
  if (Serial.available() > 0) {
    // Wait a bit for the entire message to arrive
    delay(50);
    
    // Read the whole string
    String inputString = "";
    while (Serial.available() > 0) {
      char inChar = (char)Serial.read();
      inputString += inChar;
      delay(50);
    }
    
    // Parse the string for x and y values
    int spaceIndex = inputString.indexOf(' ');
    if (spaceIndex != -1) {
      float x_dir = inputString.substring(0, spaceIndex).toFloat();
      float y_dir = inputString.substring(spaceIndex + 1).toFloat();
      
      // Echo back what was received
      Serial.print("Received x: ");
      Serial.print(x_dir, 4);
      Serial.print(", y: ");
      Serial.println(y_dir, 4);

      // Move stepper motors based on serial information
      float prevX = 0;
      float prevY = 0;

      float deltaX = x_dir - prevX;
      float deltaY = y_dir - prevY;
      
      if (deltaX != 0) {
        stepper1.step(deltaX * GEAR_RATIO);
      }

      if (deltaY != 0) {
        stepper2.step(deltaY * GEAR_RATIO);
      }
      
      prevX = x_dir;
      prevY = y_dir;
    } else {
      // Error output for unexpected format
      Serial.println("Error: Expected format 'x y'");
    }
  }
}
