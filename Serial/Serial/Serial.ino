void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  float temp = Serial.read();
  Serial.print(temp);
  // Serial.write(temp);
}
