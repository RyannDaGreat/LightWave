void setup()
{
  initializeCapSensorOutput();//Should be called during setup if using capSensor
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  Serial.begin(9600);
  setupSerialDisplay();
  updateSerialDisplay();
}
int todoNum;
void loop()
{
  updateCapSensorOutput();
  while (Serial.available())
  {
    int n = Serial.read();
    if (n >= 128)
    {
      todoNum = n;
    }
    else//n<128
    {
      if (todoNum == 128)
      {
        setFingerNumLed(n);
      }
      if (todoNum == 129)
      {
        setNumLedPerNote(n);
      }
      if (todoNum == 130)
      {
        setCurrentNoteShift(n);
      }
      todoNum = 0;
    }
  }
  // Some example procedures showing how to display to the pixels:
  //  colorWipe(strip.Color(255, 0, 0), 50); // Red
  //  colorWipe(strip.Color(0, 255, 0), 50); // Green
  //  colorWipe(strip.Color(0, 0, 255), 50); // Blue
  //  theaterChase(strip.Color(127, 127, 127), 50); // White
  //  theaterChase(strip.Color(127, 0, 0), 50); // Red
  //  theaterChase(strip.Color(0, 0, 127), 50); // Blue

  setBlankCanvas();
  updateUniformNumledMode();
  strip.show();
  //  rainbow(20);
  //  rainbowCycle(20);
  //  theaterChaseRainbow(50);
}
