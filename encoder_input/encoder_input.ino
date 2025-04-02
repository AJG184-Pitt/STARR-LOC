const uint8_t encoder_1 = 2;

void setup() {
  // initialize pins
  pinMode(encoder_1,INPUT);

  

}

void loop() {
  // put your main code here, to run repeatedly:
  int encoder_1_out = digitalRead(encoder_1);
  Serial.println(encoder_1_out);
}
