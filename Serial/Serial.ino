void setup() {
  Serial.begin(9600);
}

void loop() {
  // Check if data is available
  if (Serial.available() > 0) {
    // Wait a bit for the entire message to arrive
    delay(100);
    
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
      float x = inputString.substring(0, spaceIndex).toFloat();
      float y = inputString.substring(spaceIndex + 1).toFloat();
      
      // Echo back what was received
      Serial.print("Received x: ");
      Serial.print(x, 5);
      Serial.print(", y: ");
      Serial.println(y, 5);
    } else {
      Serial.println("Error: Expected format 'x y'");
    }
  }
}
