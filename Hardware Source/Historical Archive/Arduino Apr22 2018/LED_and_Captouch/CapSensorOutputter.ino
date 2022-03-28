const int capSensorOutputPin=13;//This pin is set to high if capsensor is touched, else low. It is read by the axoloti via digital input, not serial.
void initializeCapSensorOutput()
{
  //Should be called during setup
  pinMode(capSensorOutputPin,OUTPUT);
}
void updateCapSensorOutput()
{
  //Should be called in some loop
  digitalWrite(capSensorOutputPin,getCapSensorTouched()?HIGH:LOW);
}

