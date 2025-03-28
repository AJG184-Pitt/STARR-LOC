// libraries
#include <string.h>
#include "mpu9250.h"

// set up pin numbers
const uint8_t az_step = 5;
const uint8_t az_dir = 4;
const uint8_t el_step = 3;
const uint8_t el_dir = 2;

// steps per rotation
const float steps_per_rotation = 4450;

// define the speed of the steppers
const uint16_t stepper_delay = 1000;

/* Mpu9250 object, SPI bus, CS on pin 10 */
bfs::Mpu9250 imu(&SPI, 10);

void setup() {

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

  // set up serial connection
  Serial.begin(115200);
  while(!Serial) {}

  // initialize 9 axis sensor
  /* Start the I2C bus */
  /* Start the SPI bus */
  SPI.begin();
  //SPI.setClockDivider(1280);
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

  /*
  delay(5000);
  // gather data around the circle
  int step_size = 50;
  int az_steps = 5000/step_size;
  for(int i = 0; i < az_steps; i++){
    get_mag_data();
    az_step_control(1,step_size);
  }
  */

  // calibrate
  level();
  north();
  level();
  north();
  level();
  north();


  // move to a given angle
  // initialize variables to store where pointing at a given time
  float az_deg_curr = 0;
  float el_deg_curr = 0;
  float az_step_curr = 0;
  float el_step_curr = 0;
  float az_target = 0;
  float el_target = 0;
  float az_step_adj = 0;
  float el_step_adj = 0;

  
  while(1){
    // get target angles from the serial
    Serial.print("Input the target azimuth angle:\n");
    // wait for user input
    while(Serial.available() == 0){}
    String az_in = Serial.readString();
    az_target = az_in.toFloat(); // (-180,180]

    Serial.print("Input the target elevation angle:\n");
    // wait for user input
    while(Serial.available() == 0){}
    String el_in = Serial.readString();
    el_target = el_in.toFloat(); // (-180,180]

    // calculate steps to correct
    az_step_adj = (az_target-az_deg_curr)/360*steps_per_rotation;
    el_step_adj = (el_target-el_deg_curr)/360*steps_per_rotation;
    // move to new position
    az_step_control(az_step_adj<0,(uint16_t)round(abs(az_step_adj)));
    el_step_control(el_step_adj<0,(uint16_t)round(abs(el_step_adj)));
    // adjust internal markers
    az_deg_curr += (float)az_step_adj/steps_per_rotation*360;
    el_deg_curr += (float)el_step_adj/steps_per_rotation*360;
    az_step_curr += (float)az_step_adj;
    el_step_curr += (float)el_step_adj;

    delay(1000);
    Serial.println(get_az(),1);
  }

  while(1){
  }
}

void loop(){};

// step az motor by certain amount in certain direction
void az_step_control(bool dir, uint16_t num_steps){

  /*Serial.print("STEPS: ");
  Serial.print(num_steps);
  Serial.print("\n");*/

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
    delayMicroseconds(stepper_delay);
    digitalWrite(az_step, LOW);
    delayMicroseconds(stepper_delay);
  }
}

// step el motor by certain amount in certain direction
void el_step_control(bool dir, uint16_t num_steps){

  // set direction of rotation
  if(dir){
    digitalWrite(el_dir, LOW);
  }
  else{
    digitalWrite(el_dir, HIGH);
  }

  // handle stepping a certain number of steps
  for (uint16_t step_count = 0; step_count < num_steps; step_count++){
    digitalWrite(el_step, HIGH);
    delayMicroseconds(stepper_delay);
    digitalWrite(el_step, LOW);
    delayMicroseconds(stepper_delay);
  }
}

// handle magnetic compass
void print_raw(){
/* Check if data read */
  if (imu.Read()) {
    Serial.print(imu.new_imu_data());
    Serial.print("\t");
    Serial.print(imu.new_mag_data());
    Serial.print("\t");
    Serial.print(imu.accel_x_mps2());
    Serial.print("\t");
    Serial.print(imu.accel_y_mps2());
    Serial.print("\t");
    Serial.print(imu.accel_z_mps2());
    Serial.print("\t");
    Serial.print(imu.gyro_x_radps());
    Serial.print("\t");
    Serial.print(imu.gyro_y_radps());
    Serial.print("\t");
    Serial.print(imu.gyro_z_radps());
    Serial.print("\t");
    Serial.print(imu.mag_x_ut());
    Serial.print("\t");
    Serial.print(imu.mag_y_ut());
    Serial.print("\t");
    Serial.print(imu.mag_z_ut());
    Serial.print("\t");
    Serial.print(imu.die_temp_c());
    Serial.print("\n");
  }
}

// this function uses the accelerometer to find level
float get_el(){

  // measure the accelerometer data and average over 10 measurements
  float num_avg = 5;
  float accel_x = 0;
  float accel_y = 0;
  float accel_z = 0;

  delay(100);
  
  int i = 0;
  while(i < num_avg){
    imu.Read();
    if(imu.new_mag_data()){
      accel_x += imu.accel_x_mps2()/num_avg;
      accel_y += imu.accel_y_mps2()/num_avg;
      accel_z += imu.accel_z_mps2()/num_avg;
      i++;
    }
    else {
      delay(10);
    }
  }

  // get the elevation adjustment with the arctangent of atan(x,z)
  float el_meas = atan(accel_x/accel_z)*180/3.1415;

  return(el_meas);
}

void level(){
  float el_meas = get_el();
  // step the elevation to level
  bool dir = el_meas>0;
  uint16_t steps = (abs(el_meas)/360*steps_per_rotation);
  if(steps>10){el_step_control(dir, steps);}
 
}

// this function uses the magnetometer when level to measure current azimuth
float get_az(){

  // measure the magnetometer data and average over 100 measurements
  float num_avg = 100;
  float mag_x = 0;
  float mag_y = 0;
  float mag_z = 0;

  int i = 0;
  while(i < num_avg){
    if(imu.Read()){
      if((imu.mag_x_ut() != 0) & (imu.mag_y_ut() != 0) & (imu.mag_z_ut() != 0)){
        mag_x += imu.mag_x_ut()/num_avg;
        mag_y += imu.mag_y_ut()/num_avg;
        mag_z += imu.mag_z_ut()/num_avg;
        i++;
      }
    }
    delay(10);
  }
  
  // rescale x and y
  mag_x = (mag_x - (-61.5))/27.46;
  mag_y = (mag_y - (-198.96))/26.5;

  Serial.print(mag_x);
  Serial.print("\t");
  Serial.print(mag_y);
  Serial.print("\n");

  // get the elevation adjustment with the arctangent of atan(x,z)
  float az_meas = atan2(mag_x,mag_y)*180/3.1415 + 40;

  return(az_meas);
}

void north(){
  // step the elevation to level
  float az_meas = get_az();
  bool dir = az_meas>0;
  uint16_t steps = (abs(az_meas)/360*steps_per_rotation);
  if(steps>10){az_step_control(dir, steps);}
}


void get_mag_data(){
  // measure the accelerometer data and average over 10 measurements
  float num_avg = 200;
  float mag_x = 0;
  float mag_y = 0;
  float mag_z = 0;

  int i = 0;
  while(i < num_avg){
    if(imu.Read()){
      if((imu.mag_x_ut() != 0) & (imu.mag_y_ut() != 0) & (imu.mag_z_ut() != 0)){
        mag_x += imu.mag_x_ut()/num_avg;
        mag_y += imu.mag_y_ut()/num_avg;
        mag_z += imu.mag_z_ut()/num_avg;
        i++;
      }
    }
    delay(10);
  }

  /*Serial.print(mag_x);
  Serial.print("\t");
  Serial.print(mag_y);
  Serial.print("\t");
  Serial.print(mag_z);
  Serial.print("\n");*/
}