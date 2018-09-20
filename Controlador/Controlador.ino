//Libreraria para el display
#include <LiquidCrystal.h>

// Pines utilizados para el LCD
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

//Pines para el control joystick
int xPin = A1;
int yPin = A0;
//Variables de almacenamiento del control joystick
int xPosition = 0;
int yPosition = 0;
int buttonState = 0;

//Variables de almacenamiento de datos pacmandev
String performance = "";

void setup() {
  // inicializar las comunicaciones en serie a 9600 bps:
  Serial.begin(9600); 
  lcd.begin(16, 2);
  lcd.print("Juego: Inactivo");
  pinMode(xPin, INPUT);
  pinMode(yPin, INPUT);
}

void loop() {
  //Medicion de los valores dados por el joystick
  xPosition = analogRead(xPin);
  yPosition = analogRead(yPin);

  //Imprime los valores datos por el joystick en el puerto serial
  Serial.print(xPosition);
  Serial.print(",");
  Serial.print(yPosition);
  Serial.print(",");
  Serial.println(buttonState);

  if(Serial.available()>0){
    //performance = Serial.readString();
  }
  actualizarPanel();
  delay(50);
}

void actualizarPanel(){
  //Fija el curso en la columna 0, fila 0
  lcd.clear();
  lcd.setCursor(0, 0);
  if(performance != ""){lcd.print("Juego:Activo");}
  else{lcd.print("PACMAN AI CHALLENGE");}
  
  //Fija el curso en la columna 0, fila 1
  lcd.setCursor(0, 1);
  lcd.print("X:");
  lcd.print(xPosition);
  lcd.print(",Y:");
  lcd.print(yPosition);
}
