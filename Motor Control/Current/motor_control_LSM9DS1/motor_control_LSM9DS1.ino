// STARR-LOC
// Authors: Adam Nichols, Thomas Eckrich
// ECE 1896
// Spring 2025


// libraries
#include <string.h>
#include "SPI.h"
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h>


// set up pin numbers
const uint8_t az_step_pin = 33;
const uint8_t az_dir_pin = 12;
const uint8_t el_step_pin = 27;
const uint8_t el_dir_pin = 14;

// number of steps in a revolution
const float steps_per_revolution = 4450;

// i2c init for imu
Adafruit_LSM9DS1 lsm = Adafruit_LSM9DS1();

// default delay
const int default_delay = 5;

/*************************************************************************************************/
/*************************************************************************************************/

// initialize internally stored position information
float az_step_curr = 0;
float el_step_curr = 0;
float az_deg_curr = 0;
float el_deg_curr = 0;

void setup() {

  // set up pins as input/output
  pinMode(az_step_pin, OUTPUT);
  pinMode(az_dir_pin, OUTPUT);
  pinMode(el_step_pin, OUTPUT);
  pinMode(el_dir_pin, OUTPUT);

  // initialize pins
  digitalWrite(az_step_pin, LOW);
  digitalWrite(az_dir_pin, LOW);
  digitalWrite(el_step_pin, LOW);
  digitalWrite(el_dir_pin, LOW);

   /* Serial to display data */
  Serial.begin(115200);
  while(!Serial) {delay(1);}

  Wire.begin();
  // init imu
  // Try to initialise and warn if we couldn't detect the chip
  if (!lsm.begin())
  {
    Serial.println("Unable to initialize the LSM9DS1. Check your wiring!");
    while (1);
  }
  //Serial.println("Found LSM9DS1 9DOF");

  // helper to just set the default scaling we want, see above!
  setupSensor();

  // calibrate: find level and north
  level();
  north();

  // do north again if error more than 5 degrees
  if(get_az() > 5){north();};



}

/*************************************************************************************************/
/*************************************************************************************************/

void loop(){

  // check if there is available data
  int available_bytes = Serial.available();
  if (available_bytes > 0){

    char serial_input[32];
    for(int i = 0; i < available_bytes; i++){
      serial_input[i] = Serial.read();
    }

    // parse string to separate az/el angles
    char* token = NULL;
    const char delim[] = " ";

    // tokenize the string
    char* az_target_str = strtok(serial_input, delim);
    char* el_target_str = strtok(NULL, delim);
    char* dur_str = strtok(NULL, delim);

    // type conversion
    float az_deg_target = az_deg_curr;
    float el_deg_target = el_deg_curr;
    float dur = 0;

    if (az_target_str != NULL) { az_deg_target = atof(az_target_str);}
    if (el_target_str != NULL) { el_deg_target = atof(el_target_str);}
    if (dur_str != NULL) { dur = atof(dur_str);}

    move_to_angle(az_deg_target, el_deg_target, dur);
  }
}

/*************************************************************************************************/
/*************************************************************************************************/

void setupSensor()
{
  // 1.) Set the accelerometer range
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_10HZ);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_4G, lsm.LSM9DS1_ACCELDATARATE_119HZ);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_8G, lsm.LSM9DS1_ACCELDATARATE_476HZ);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_16G, lsm.LSM9DS1_ACCELDATARATE_952HZ);
  
  // 2.) Set the magnetometer sensitivity
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_8GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_12GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_16GAUSS);

  // 3.) Setup the gyroscope
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
  //lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_500DPS);
  //lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_2000DPS);
}


// step az motor by certain amount in certain direction
void az_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){ digitalWrite(az_dir_pin, HIGH);}
  else{ digitalWrite(az_dir_pin, LOW);}

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(az_step_pin, HIGH);
    delay(default_delay);
    digitalWrite(az_step_pin, LOW);
    delay(default_delay);
  }
}

// step el motor by certain amount in certain direction
void el_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){ digitalWrite(el_dir_pin, HIGH);}
  else{ digitalWrite(el_dir_pin, LOW); }

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(el_step_pin, HIGH);
    delay(default_delay);
    digitalWrite(el_step_pin, LOW);
    delay(default_delay);
  }
}

// move both az and el at same time, finish by moving just along longer measurement
void azel_step_control_dly(bool az_dir, uint16_t az_steps, bool el_dir, uint16_t el_steps, float dly){

  // set direction of rotation
  if(az_dir){ digitalWrite(az_dir_pin, HIGH);}
  else{ digitalWrite(az_dir_pin, LOW);}

  // set direction of rotation
  if(el_dir){ digitalWrite(el_dir_pin, HIGH);}
  else{ digitalWrite(el_dir_pin, LOW); }

  // calculate the delay needed
  // find larger number of steps
  uint16_t max_steps = 0;
  if(az_steps > el_steps) {
    max_steps = az_steps;
  }
  else{
    max_steps = el_steps;
  }
  // calculate the delay
  uint32_t dly_us = floor(dly * 500000 / max_steps);
  if (dly_us < default_delay*1000) {dly_us = default_delay*1000;} // make sure delay is at least 5000us

  // handle stepping a certain number of steps
  uint16_t az_step_curr = az_steps;
  uint16_t el_step_curr = el_steps;

  while ((az_step_curr > 0) & (el_step_curr > 0)){
    digitalWrite(az_step_pin, HIGH);
    digitalWrite(el_step_pin, HIGH);
    delayMicroseconds(dly_us);
    digitalWrite(az_step_pin, LOW);
    digitalWrite(el_step_pin, LOW);
    delayMicroseconds(dly_us);
    az_step_curr--;
    el_step_curr--;
  }

  // finish the rest of the motion on one axis
  if(az_step_curr > 0){   

    // handle stepping a certain number of steps
    for (uint16_t step_count = 0; step_count < az_step_curr; step_count++){
      digitalWrite(az_step_pin, HIGH);
      delayMicroseconds(dly_us);
      digitalWrite(az_step_pin, LOW);
      delayMicroseconds(dly_us);
    }
  }

  if(el_step_curr > 0){

    // handle stepping a certain number of steps
    for (uint16_t step_count = 0; step_count < el_step_curr; step_count++){
      digitalWrite(el_step_pin, HIGH);
      delayMicroseconds(dly_us);
      digitalWrite(el_step_pin, LOW);
      delayMicroseconds(dly_us);
    }
  }

}

// move both az and el at same time, finish by moving just along longer measurement
void azel_step_control(bool az_dir, uint16_t az_steps, bool el_dir, uint16_t el_steps){

  // set direction of rotation
  if(az_dir){ digitalWrite(az_dir_pin, HIGH);}
  else{ digitalWrite(az_dir_pin, LOW);}

  // set direction of rotation
  if(el_dir){ digitalWrite(el_dir_pin, HIGH);}
  else{ digitalWrite(el_dir_pin, LOW); }

  // handle stepping a certain number of steps
  uint16_t az_step_curr = az_steps;
  uint16_t el_step_curr = el_steps;
  
  while ((az_step_curr > 0) & (el_step_curr > 0)){
    digitalWrite(az_step_pin, HIGH);
    digitalWrite(el_step_pin, HIGH);
    delay(default_delay);
    digitalWrite(az_step_pin, LOW);
    digitalWrite(el_step_pin, LOW);
    delay(default_delay);
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
      // read sensor
      lsm.read();
      sensors_event_t a, m, g, temp;
      lsm.getEvent(&a, &m, &g, &temp); 

      // avg
      mag_x += m.magnetic.x/num_avg;
      mag_y += m.magnetic.y/num_avg;
      mag_z += m.magnetic.z/num_avg;
      i++;
    }

    // remove dc offset and scale to -1 to 1
    mag_x = (mag_x - (149.6))/29;
    mag_y = (mag_y - (7.3))/26.6;

    // get the elevation from the atan function
    float declination = -35;
    float az_meas = atan2(mag_x,-mag_y)*180/3.1415 + declination;

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
      // read the sensor
      lsm.read();
      sensors_event_t a, m, g, temp;
      lsm.getEvent(&a, &m, &g, &temp); 

      accel_x += a.acceleration.x/num_avg;
      accel_y += a.acceleration.y/num_avg;
      accel_z += a.acceleration.z/num_avg;
      i++;
    }

    // get the elevation from the atan function
    float el_meas = atan(accel_y/accel_z)*180/3.1415;

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
  //Serial.println(az_curr,1);

  // correct for the error in elevation
  bool az_dir = az_curr > 0;
  int16_t az_steps_abs = (int16_t)round(abs(az_curr/360*steps_per_revolution));
  if(az_steps_abs > 5){ az_step_control(az_dir, az_steps_abs);}
  
  /*
  // rotate half a rotation
  az_step_control(0,steps_per_revolution/2);

  // move around until finding maximum on x
  float max_x = 1000000;
  uint16_t az_max_x = 0;
  uint16_t az_step = 0;
  uint16_t az_step_inc = 45;
  while(az_step < steps_per_revolution){

    // average x measurement across 100 measurements
    uint8_t num_avg = 1;
    float mag_x = 0;
    // get measurement from accelerometer, average over multiple readings
    uint8_t i = 0;
    while(i < num_avg){
      if(imu.Read()){
        if ((imu.mag_x_ut() != 0) & (imu.mag_y_ut() != 0) & (imu.mag_z_ut() != 0) ){
          mag_x += imu.mag_x_ut()/num_avg;
          i++;
        }
      }
    }

    // save max and step where it occured
    if (mag_x < max_x){ 
      max_x = mag_x;
      az_max_x = az_step;
    }
    Serial.print(az_step);
    Serial.print("\t");
    Serial.print(mag_x);
    Serial.print("\n");

    // move to next step
    az_step_control(1,az_step_inc);

    // increment the step
    az_step += az_step_inc;
  }

  // move to where max was recorded
  // account for declination
  uint16_t declination_steps = steps_per_revolution*(9.5/360);
  az_step_control(0,az_step-az_max_x);//-declination_steps);

  Serial.print("\nMax:\n");
  Serial.print(az_step-az_max_x);
  Serial.print("\t");
  Serial.print(max_x);
  Serial.print("\n");
*/
}


void move_to_angle(float az_deg_target, float el_deg_target, float dur){

    // find closest reference angle within -270 to 270
    if( abs(az_deg_curr - (az_deg_target)) > abs(az_deg_curr - (az_deg_target + 360)) ){
      az_deg_target += 360;
    }

    else if( abs(az_deg_curr - (az_deg_target)) > abs(az_deg_curr - (az_deg_target - 360)) ){
      az_deg_target -= 360;
    }

    // make sure target within bounds
    if( az_deg_target > 270) { az_deg_target -= 360;}
    else if( az_deg_target < -270) { az_deg_target += 360;}

    if( (az_deg_target <= 270) & (az_deg_target >= -270) & (el_deg_target >= 0) & (el_deg_target <= 90)) {

      // get azimuth step adjustment from angle difference
      float az_deg_adj = az_deg_target - az_deg_curr;
      uint16_t az_step_adj = (uint16_t)round(abs(az_deg_adj/360*steps_per_revolution));
      bool az_dir = az_deg_adj < 0;

      // get elevation step adjustment from angle difference
      float el_deg_adj = el_deg_target - el_deg_curr;
      uint16_t el_step_adj = (uint16_t)round(abs(el_deg_adj/360*steps_per_revolution));
      bool el_dir = el_deg_adj < 0;

      // move
      azel_step_control_dly(az_dir,az_step_adj,el_dir,el_step_adj,dur);

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
    else{
      Serial.print("Error! Input out of bounds!\n");
    }
}

/*
// calibrate magnetic compass offsets
void mag_cali(){
  
  // spin around the circle and print out mag measurements
  uint16_t az_step_inc = 100;
  uint16_t az_step = 0;

  // keep the max and min of the x and y vals
  float mag_x_max = -1000000;
  float mag_x_min = 1000000;
  float mag_y_max = -1000000;
  float mag_y_min = 1000000;

  while(az_step < steps_per_revolution){

    // initialize variables
    uint8_t num_avg = 10;
    float mag_x = 0;
    float mag_y = 0;
    float mag_z = 0;

    // get measurement from accelerometer, average over multiple readings
    uint8_t i = 0;
    while(i < num_avg){
      // read sensor
      lsm.read();
      sensors_event_t a, m, g, temp;
      lsm.getEvent(&a, &m, &g, &temp); 

      // avg
      mag_x += m.magnetic.x/num_avg;
      mag_y += m.magnetic.y/num_avg;
      mag_z += m.magnetic.z/num_avg;

      i++;
    }

    // check if max or min found
    if(mag_x > mag_x_max){mag_x_max = mag_x;}
    if(mag_x < mag_x_min){mag_x_min = mag_x;}
    if(mag_y > mag_y_max){mag_y_max = mag_y;}
    if(mag_y < mag_y_min){mag_y_min = mag_y;}

    // move
    az_step_control(1,az_step_inc);

    // increment step number
    az_step += az_step_inc;
  }

  // calculate offsets and scaling for x and y
  float mag_x_offset = (mag_x_max+mag_x_min)/2;
  float mag_y_offset = (mag_y_max+mag_y_min)/2;
  float mag_x_scale = (mag_x_max-mag_x_min)/2;
  float mag_y_scale = (mag_y_max-mag_y_min)/2;

  // print outputs
  Serial.println(mag_x_offset,1);
  Serial.println(mag_y_offset,1);
  Serial.println(mag_x_scale,1);
  Serial.println(mag_y_scale,1);
}
*/
