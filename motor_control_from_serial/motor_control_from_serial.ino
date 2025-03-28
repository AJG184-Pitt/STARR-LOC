// libraries
#include <string.h>
#include "mpu9250.h"

// set up pin numbers
const uint8_t az_step = 5;
const uint8_t az_dir_pin = 4;
const uint8_t el_step = 3;
const uint8_t el_dir_pin = 2;

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
    mag_x = (mag_x - (-61.5))/27.46;
    mag_y = (mag_y - (-198.96))/26.5;

    // get the elevation from the atan function
    float az_meas = atan(mag_x/mag_y);

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
        accel_y += imu.accel_x_mps2()/num_avg;
        accel_z += imu.accel_x_mps2()/num_avg;
        i++;
      }
    }

    // get the elevation from the atan function
    float el_meas = atan(accel_x/accel_z);

    return el_meas;
}

// find level
void level(){
  
  // get the current elevation measurement
  float el_curr = get_el();

  // correct for the error in elevation
  bool el_dir = el_curr > 0;
  int16_t el_steps_abs = (int16_t)round(abs())
}

