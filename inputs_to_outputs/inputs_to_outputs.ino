#include <Stepper.h>

int pinA = 2;   // Connected to CLK on KY-040
int pinB = 3;   // Connected to DT on KY-040
int pinC = A0;  // Connected to analog pin

const int STEPPER_STEPS = 32;
const int GEAR_RATIO = 64;
const int MIN_STEP_THRESHOLD = 5;
const float STEP_MULTIPLIER = 3.2;

int encoderPosCount = 0;
int pinALast;
int aVal;
boolean bCW;
int current_position_stepper1 = 0;
int previous_slider = 0;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;  // ms

// Need to multiply steps by 64 due to the gear ratio
Stepper stepper1(STEPPER_STEPS, 4, 6, 5, 7);
Stepper stepper2(STEPPER_STEPS, 8, 10, 9, 11);

void setup() {
  pinMode(pinA, INPUT);
  pinMode(pinB, INPUT);
  pinMode(pinC, INPUT_PULLUP);
  stepper1.setSpeed(200);
  stepper2.setSpeed(200);
  pinALast = digitalRead(pinA);
  previous_slider = analogRead(pinC);
  Serial.begin(9600);
}

void loop() {
  aVal = digitalRead(pinA);
  int slider_value = analogRead(pinC);
  
  // Calculate target position for stepper 2
  int target_position_stepper2 = map(slider_value, 0, 1023, -STEPPER_STEPS, STEPPER_STEPS);
  int steps_to_move_stepper2 = target_position_stepper2 - current_position_stepper1;

  int steps_to_move_stepper1 = STEP_MULTIPLIER * GEAR_RATIO;

  // int val = 0
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (aVal != pinALast) {  // Means the knob is rotating
      lastDebounceTime = millis();
      // if the knob is rotating, we need to determine direction
      // We do that by reading pin B.
      if (digitalRead(pinB) != aVal) {  // Means pin A Changed first - We're Rotating Clockwise.
        //encoderPosCount++;
        bCW = true;
        steps_to_move_stepper1 = (int)(STEP_MULTIPLIER * GEAR_RATIO);
      } else {  // Otherwise B changed first and we're moving CCW
        bCW = false;
        //encoderPosCount--;
        steps_to_move_stepper1 = -(int)(STEP_MULTIPLIER * GEAR_RATIO);
      }
      
      // if (!bCW) {
      //   steps_to_move_stepper1 = -steps_to_move_stepper1;
      // }

      stepper1.step(steps_to_move_stepper1);
      current_position_stepper1 += bCW ? steps_to_move_stepper1 : -steps_to_move_stepper1;

      Serial.print("Rotated: ");
      Serial.println(bCW ? "clockwise" : "counterclockwise");
      Serial.print("Encoder Position: ");
      Serial.println(encoderPosCount);
    }
  }

  // Handle slider movement for stepper2
  if (abs(slider_value - previous_slider) > MIN_STEP_THRESHOLD) {
    stepper2.step(steps_to_move_stepper2 * 64);
    current_position_stepper1 += steps_to_move_stepper2;  // Update the tracked position

    Serial.print("Slider Value: ");
    Serial.println(slider_value);
    Serial.print("Steps moved (Stepper 2): ");
    Serial.println(steps_to_move_stepper2);

    previous_slider = slider_value;
  }

  pinALast = aVal;
}
