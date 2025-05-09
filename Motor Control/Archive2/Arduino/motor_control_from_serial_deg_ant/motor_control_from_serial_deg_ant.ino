// libraries
#include <string.h>
#include "mpu9250.h"

// set up pin numbers
const uint8_t az_step = 5;
const uint8_t az_dir_pin = 4;
const uint8_t el_step = 3;
const uint8_t el_dir_pin = 2;

// number of steps in a revolution
const float steps_per_revolution = 4450;

/* Mpu9250 object, SPI bus, CS on pin 10 */
bfs::Mpu9250 imu(&SPI, 10);

void setup() {

  // set up pins as input/output
  pinMode(az_step, OUTPUT);
  pinMode(az_dir_pin, OUTPUT);
  pinMode(el_step, OUTPUT);
  pinMode(el_dir_pin, OUTPUT);

  // initialize pins
  digitalWrite(az_step, LOW);
  digitalWrite(az_dir_pin, LOW);
  digitalWrite(el_step, LOW);
  digitalWrite(el_dir_pin, LOW);

   /* Serial to display data */
  Serial.begin(115200);
  while(!Serial) {}
  /* Start the SPI bus */
  SPI.begin();
  /* Initialize and configure IMU */
  if (!imu.Begin()) {
    Serial.println("Error initializing communication with IMU");
    while(1) {}
  }
  /* Set the sample rate divider */
  if (!imu.ConfigSrd(0)) {
    Serial.println("Error configured SRD");
    while(1) {}
  }


  level();
  north();


  // initialize internally stored position information
  float az_step_curr = 0;
  float el_step_curr = 0;
  float az_deg_curr = 0;
  float el_deg_curr = 0;

  while(1){

    // get angles from serial and put into string
    //Serial.print("\nInput Angles in format <az> <el>:\n");
    while(Serial.available() == 0){}
    String serial_input = Serial.readString();

    // parse string to separate az/el angles
    int space_pos = serial_input.indexOf(' ');
    String az_target_str = serial_input.substring(0, space_pos);
    String el_target_str = serial_input.substring(space_pos + 1);
    float az_deg_target = az_target_str.toFloat();
    float el_deg_target = el_target_str.toFloat();

    // get azimuth step adjustment from angle difference
    float az_deg_adj = az_deg_target - az_deg_curr;
    uint16_t az_step_adj = (uint16_t)round(abs(az_deg_adj/360*steps_per_revolution));
    bool az_dir = az_deg_adj < 0;

    // get elevation step adjustment from angle difference
    float el_deg_adj = el_deg_target - el_deg_curr;
    uint16_t el_step_adj = (uint16_t)round(abs(el_deg_adj/360*steps_per_revolution));
    bool el_dir = el_deg_adj < 0;

    // move
    azel_step_control(az_dir,az_step_adj,el_dir,el_step_adj);

    // update to current position
    if (az_deg_adj >= 0){
      az_step_curr += az_step_adj;
      az_deg_curr += (float)az_step_adj/steps_per_revolution*360;
    }
    else{
      az_step_curr -= az_step_adj;
      az_deg_curr -= (float)az_step_adj/steps_per_revolution*360;
    }

    if (el_deg_adj >= 0){
      el_step_curr += el_step_adj;
      el_deg_curr += (float)el_step_adj/steps_per_revolution*360;
    }
    else{
      el_step_curr -= el_step_adj;
      el_deg_curr -= (float)el_step_adj/steps_per_revolution*360;
    }


  }

  Serial.print("Error! Hanging in dead while loop.\n");
  while(1){}
}

void loop(){};

// step az motor by certain amount in certain direction
void az_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){ digitalWrite(az_dir_pin, LOW);}
  else{ digitalWrite(az_dir_pin, HIGH);}

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(az_step, HIGH);
    delay(1);
    digitalWrite(az_step, LOW);
    delay(1);
  }
}

// step el motor by certain amount in certain direction
void el_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){ digitalWrite(el_dir_pin, LOW);}
  else{ digitalWrite(el_dir_pin, HIGH); }

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(el_step, HIGH);
    delay(1);
    digitalWrite(el_step, LOW);
    delay(1);
  }
}

// move both az and el at same time, finish by moving just along longer measurement
void azel_step_control(bool az_dir, uint16_t az_steps, bool el_dir, uint16_t el_steps){

  // set direction of rotation
  if(az_dir){ digitalWrite(az_dir_pin, LOW);}
  else{ digitalWrite(az_dir_pin, HIGH);}

  // set direction of rotation
  if(el_dir){ digitalWrite(el_dir_pin, LOW);}
  else{ digitalWrite(el_dir_pin, HIGH); }

  // handle stepping a certain number of steps
  uint16_t az_step_curr = az_steps;
  uint16_t el_step_curr = el_steps;
  
  while ((az_step_curr > 0) & (el_step_curr > 0)){
    digitalWrite(az_step, HIGH);
    digitalWrite(el_step, HIGH);
    delay(1);
    digitalWrite(az_step, LOW);
    digitalWrite(el_step, LOW);
    delay(1);
    az_step_curr--;
    el_step_curr--;
  }

  // finish the rest of the motion on one axis
  if(az_step_curr > 0){ az_step_control(az_dir, az_step_curr);}
  if(el_step_curr > 0){ el_step_control(el_dir, el_step_curr);}

}

// when level, get the current azimuth measurement
float get_az(){

    // initialize variables
    uint8_t num_avg = 100;
    float mag_x = 0;
    float mag_y = 0;
    float mag_z = 0;

    // get measurement from accelerometer, average over multiple readings
    uint8_t i = 0;
    while(i < num_avg){
      if(imu.Read()){
        if ((imu.mag_x_ut() != 0) & (imu.mag_y_ut() != 0) & (imu.mag_z_ut() != 0) ){
          mag_x += imu.mag_x_ut()/num_avg;
          mag_y += imu.mag_y_ut()/num_avg;
          mag_z += imu.mag_z_ut()/num_avg;
          i++;
        }
      }
    }

    // remove dc offset and scale to -1 to 1
    mag_x = (mag_x - (-87.64))/24.59;
    mag_y = (mag_y - (-233.805))/24.965;

    // get the elevation from the atan function
    float declination = 30;
    float az_meas = atan2(mag_x,mag_y)*180/3.1415 + declination;

    return az_meas;
}

// when get the current elevation angle
float get_el(){

    // initialize variables
    uint8_t num_avg = 10;
    float accel_x = 0;
    float accel_y = 0;
    float accel_z = 0;

    // get measurement from accelerometer, average over multiple readings
    uint8_t i = 0;
    while(i < num_avg){
      if(imu.Read()){
        accel_x += imu.accel_x_mps2()/num_avg;
        accel_y += imu.accel_y_mps2()/num_avg;
        accel_z += imu.accel_z_mps2()/num_avg;
        i++;
      }
    }

    // get the elevation from the atan function
    float el_meas = atan(accel_x/accel_z)*-180/3.1415;

    return el_meas;
}

// find level
void level(){
  
  // get the current elevation measurement
  float el_curr = get_el();

  // correct for the error in elevation
  bool el_dir = el_curr < 0;
  int16_t el_steps_abs = (int16_t)round(abs(el_curr/360*steps_per_revolution));
  if(el_steps_abs > 5){ el_step_control(el_dir, el_steps_abs);}
}

// find north when level
void north(){

  // get the current azimuth angle
  float az_curr = get_az();

  // correct for the error in elevation
  bool az_dir = az_curr > 0;
  int16_t az_steps_abs = (int16_t)round(abs(az_curr/360*steps_per_revolution));
  if(az_steps_abs > 5){ az_step_control(az_dir, az_steps_abs);}
}

