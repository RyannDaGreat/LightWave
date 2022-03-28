#include <Wire.h>
#include <LiquidCrystal_I2C.h> // Using version 1.2.1
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);
void setupSerialDisplay()
{
  lcd.begin(16, 2); // sixteen characters across - 2 lines
  lcd.backlight();
}
void setSerialDisplayText(String str,int line=0)
{
  lcd.setCursor(0, line);
  lcd.print(str);
}
int currentNoteShift=0;

void updateSerialDisplay()
{
  setSerialDisplayText("    Luxwave     ",0);
  setSerialDisplayText("                ",1);
  setSerialDisplayText("Key:    "+noteName(currentNoteShift),2);
}
void setCurrentNoteShift(int n)
{
  currentNoteShift=n;
  updateSerialDisplay();
}
String noteName(int n)
{
  switch (n%12)
  {
    case 0 : return "A       ";
    case 1 : return "A# or Bb";
    case 2 : return "B       ";
    case 3 : return "C       ";
    case 4 : return "C# or Db";
    case 5 : return "D       ";
    case 6 : return "D# or Eb";
    case 7 : return "E       ";
    case 8 : return "F       ";
    case 9 : return "F# or Gb";
    case 10: return "G       ";
    case 11: return "G# or Ab";
  }
}
//DEMO CODE FOR SERIAL DISPLAY (NOT ACTUALLY PART OF LIGHTWAVE):---------------------------------------------------------------------------------
//void setup()
//{
//  lcd.begin(16, 2); // sixteen characters across - 2 lines
//  lcd.backlight();
//  // first character - 1st line
//  lcd.setCursor(0, 0);
//  lcd.print("Hello World!");
//  lcd.createChar(0, smiley);
//  lcd.write(byte(0));
//  // 8th character - 2nd line
//  lcd.setCursor(8, 1);
//  lcd.print("---asdasdasdasdasd----");
//  Serial.begin(9600);
//
//}
//byte smiley[8] = {
  //  B00000,
  //  B10001,
  //  B00000,
  //  B00000,
  //  B10001,
  //  B01110,
  //  B00000,
  //};
  //
  ////void setup() {
  ////  lcd.createChar(0, smiley);
  ////  lcd.begin(16, 2);
  ////  lcd.write(byte(0));
  ////}
  ////
