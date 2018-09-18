int xPin = A1;
int yPin = A0;
int buttonPin = 2;

int xPosition = 0;
int yPosition = 0;
int buttonState = 0;
void setup() {
  // inicializar las comunicaciones en serie a 9600 bps:
  Serial.begin(9600); 
  
  pinMode(xPin, INPUT);
  pinMode(yPin, INPUT);

  //activar resistencia pull-up en el pin pulsador 7
  pinMode(buttonPin, INPUT_PULLUP); 
  
  // Para las versiones anteriores a 1.0.1 Arduino 
  // pinMode (buttonPin, INPUT); 
  // digitalWrite (buttonPin, HIGH);
  
}

void loop() {
  xPosition = analogRead(xPin);
  yPosition = analogRead(yPin);
  buttonState = digitalRead(buttonPin);
  
  Serial.print(xPosition);
  Serial.print(",");
  Serial.print(yPosition);
  Serial.print(",");
  Serial.println(buttonState);
  delay(100);
}
