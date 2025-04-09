
// libraries
#include <string.h>
#include <Wire.h>
#include <SparkFun_MMC5983MA_Arduino_Library.h>

// serial connection
const int serial_rate = 9600;

// set up pin numbers
const uint8_t az_step = 9;
const uint8_t az_dir = 8;
const uint8_t el_step = 11;
const uint8_t el_dir = 10;

// initialize magnetic compass
SFE_MMC5983MA Mag;

// function prototypes
void az_step_control(bool, uint16_t);
double get_az();
void print_raw();

int main() {

  // initialize arduino
  init();

  // set up serial connection
  Serial.begin(serial_rate);


  // initialize magnetic compass
  Wire.begin();

    if (Mag.begin() == false)
    {
        Serial.println("MMC5983MA did not respond - check your wiring. Freezing.");
        while (true)
            ;
    }
  Mag.softReset();
  Serial.println("MMC5983MA connected\n");


  // set up pins as input/output
  pinMode(az_step, OUTPUT);
  pinMode(az_dir, OUTPUT);
  pinMode(el_step, OUTPUT);
  pinMode(el_dir, OUTPUT);

  // initialize pins
  digitalWrite(az_step, LOW);
  digitalWrite(az_dir, LOW);
  digitalWrite(el_step, LOW);
  digitalWrite(el_dir, LOW);

  while(1){
    // wait for user input
    while(Serial.available() == 0){}
    String user_input = Serial.readString();
    double az_target = user_input.toDouble(); // (-180,180]

    // rotate the stepper motor to north
    double az_curr = 0;
    az_curr = get_az();

    bool dir = az_curr > az_target;
    uint16_t num_steps = 0;
    double full_rotation = 4900;
    num_steps = abs(round((az_curr - az_target)/360*full_rotation));

    
    Serial.print("\nAz: ");
    Serial.print(az_curr);
    Serial.print("\nDir: ");
    Serial.print(dir);
    Serial.print("\nSteps: ");
    Serial.print(num_steps);
    Serial.print("\n");
    az_step_control(dir, num_steps);

    az_curr = get_az();
    Serial.print("Az: ");
    Serial.print(az_curr);
    Serial.print("\n");
  }

  delay(100);
  return 0;
}


// step az motor by certain amount in certain direction
void az_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){
    digitalWrite(az_dir, LOW);
  }
  else{
    digitalWrite(az_dir, HIGH);
  }

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(az_step, HIGH);
    delay(1);
    digitalWrite(az_step, LOW);
    delay(1);
  }
}

// handle magnetic compass
double get_az(){

    // initialize variables
    uint32_t rawValueX = 0;
    uint32_t rawValueY = 0;
    uint32_t rawValueZ = 0;

    // Read all three channels simultaneously
    uint8_t num_avg = 10;
    uint32_t avg_x = 0;
    uint32_t avg_y = 0;
    uint32_t avg_z = 0;
    // run num_avg measurements and get the average
    for(uint8_t count = 0; count < num_avg; count++){
      Mag.getMeasurementXYZ(&rawValueX, &rawValueY, &rawValueZ);
      avg_x += rawValueX / num_avg;
      avg_y += rawValueY / num_avg;
      avg_z += rawValueZ / num_avg;
    }

    // convert raw x/y into heading
    // define hard coded constants
    // got declination from https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm
    double declination = -9.25; // [degrees] at 40.4375N, 79.958W
    double x_offset = 134212;
    double x_scale = 3178;
    double y_offset = 138990;
    double y_scale = 3317;

    // convert raw
    double x = (avg_x - x_offset)/x_scale;
    double y = (avg_y - y_offset)/y_scale;

    // use arc tangent to get heading
    double az = atan2(-y,x)*180/3.1415 + declination;

    return az;
}

// handle magnetic compass
void print_raw(){
    // initialize variables
    uint32_t rawValueX = 0;
    uint32_t rawValueY = 0;
    uint32_t rawValueZ = 0;

    // Read all three channels simultaneously
    uint16_t num_avg = 10;
    uint32_t avg_x = 0;
    uint32_t avg_y = 0;
    uint32_t avg_z = 0;
    // run num_avg measurements and get the average
    for(uint16_t count = 0; count < num_avg; count++){
      Mag.getMeasurementXYZ(&rawValueX, &rawValueY, &rawValueZ);
      avg_x += rawValueX / num_avg;
      avg_y += rawValueY / num_avg;
      avg_z += rawValueZ / num_avg;
    }

    Serial.print("X: ");
    Serial.print(avg_x);
    Serial.print("\tY: ");
    Serial.print(avg_y);
    Serial.print("\tZ: ");
    Serial.print(avg_z);
    Serial.print("\n");
}