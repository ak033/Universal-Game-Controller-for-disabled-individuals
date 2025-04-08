void setup() {
  Serial.begin(9600); //Start serial communication at 9600 baud rate 
}

void loop() {
  //Repeatedly run this code to read the sensor
  int muscleSignal = analogRead(A0);  // Read the processed muscle signal from A0
  Serial.println(muscleSignal);       // Output the value to the serial port
  delay(10);                          // Short delay to allow a smooth update on the plot
}

